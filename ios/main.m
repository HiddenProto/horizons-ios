// HORIZONS for iPad / iPhone.
//
// The whole app is one WKWebView. The page (web/) runs the real Python game in Pyodide; this
// file only does the three things a page cannot do for itself:
//   1. serve the bundle over hzapp:// so fetch() and WebAssembly work (file:// blocks both),
//   2. keep the save files in the app's Documents folder, where they survive updates and
//      show up in the Files app,
//   3. hand those saves back to the page before it starts, as window.__HZ_SAVED.
//
// Built with plain clang on a macOS CI runner - no Xcode project, no storyboard.

#import <UIKit/UIKit.h>
#import <WebKit/WebKit.h>

static NSString *const kScheme = @"hzapp";

static NSString *SavesDir(void) {
    NSString *docs = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES).firstObject;
    NSString *dir = [docs stringByAppendingPathComponent:@"stuff"];
    [[NSFileManager defaultManager] createDirectoryAtPath:dir withIntermediateDirectories:YES attributes:nil error:nil];
    return dir;
}

static BOOL SafeName(NSString *name) {
    if (name.length == 0 || name.length > 128 || [name hasPrefix:@"."]) return NO;
    NSCharacterSet *bad = [[NSCharacterSet characterSetWithCharactersInString:
        @"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"] invertedSet];
    return [name rangeOfCharacterFromSet:bad].location == NSNotFound;
}

static NSString *MimeFor(NSString *ext) {
    static NSDictionary *m;
    static dispatch_once_t once;
    dispatch_once(&once, ^{
        m = @{@"html": @"text/html", @"js": @"text/javascript", @"mjs": @"text/javascript",
              @"css": @"text/css", @"json": @"application/json", @"wasm": @"application/wasm",
              @"zip": @"application/zip", @"png": @"image/png", @"svg": @"image/svg+xml",
              @"py": @"text/plain", @"txt": @"text/plain"};
    });
    return m[ext.lowercaseString] ?: @"application/octet-stream";
}

// ---------------------------------------------------------------- hzapp:// -> bundle/web
@interface BundleScheme : NSObject <WKURLSchemeHandler>
@end

@implementation BundleScheme
- (void)webView:(WKWebView *)webView startURLSchemeTask:(id<WKURLSchemeTask>)task {
    NSString *path = task.request.URL.path;
    if (path.length == 0 || [path isEqualToString:@"/"]) path = @"/index.html";
    NSString *root = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"web"];
    NSString *file = [[root stringByAppendingPathComponent:path] stringByStandardizingPath];
    NSData *data = [file hasPrefix:root] ? [NSData dataWithContentsOfFile:file] : nil;
    if (!data) {
        NSHTTPURLResponse *r = [[NSHTTPURLResponse alloc] initWithURL:task.request.URL statusCode:404
                                                          HTTPVersion:@"HTTP/1.1" headerFields:@{}];
        [task didReceiveResponse:r];
        [task didReceiveData:[NSData data]];
        [task didFinish];
        return;
    }
    NSDictionary *headers = @{@"Content-Type": MimeFor(file.pathExtension),
                              @"Content-Length": [NSString stringWithFormat:@"%lu", (unsigned long)data.length],
                              @"Access-Control-Allow-Origin": @"*",
                              @"Cache-Control": @"no-cache"};
    NSHTTPURLResponse *r = [[NSHTTPURLResponse alloc] initWithURL:task.request.URL statusCode:200
                                                      HTTPVersion:@"HTTP/1.1" headerFields:headers];
    [task didReceiveResponse:r];
    [task didReceiveData:data];
    [task didFinish];
}
- (void)webView:(WKWebView *)webView stopURLSchemeTask:(id<WKURLSchemeTask>)task {}
@end

// ---------------------------------------------------------------- the one screen
@interface GameController : UIViewController <WKScriptMessageHandler>
@property (nonatomic, strong) WKWebView *web;
@end

@implementation GameController

- (NSString *)savedAsScript {
    NSMutableDictionary *out = [NSMutableDictionary dictionary];
    NSString *dir = SavesDir();
    for (NSString *name in [[NSFileManager defaultManager] contentsOfDirectoryAtPath:dir error:nil]) {
        if (!SafeName(name) || [name hasSuffix:@".tmp"]) continue;
        NSString *text = [NSString stringWithContentsOfFile:[dir stringByAppendingPathComponent:name]
                                                   encoding:NSUTF8StringEncoding error:nil];
        if (text) out[name] = text;
    }
    NSData *json = [NSJSONSerialization dataWithJSONObject:out options:0 error:nil];
    NSString *s = json ? [[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding] : @"{}";
    return [NSString stringWithFormat:@"window.__HZ_SAVED = %@;", s];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    UIColor *bg = [UIColor colorWithRed:0x0b/255.0 green:0x0a/255.0 blue:0x09/255.0 alpha:1];
    self.view.backgroundColor = bg;

    WKWebViewConfiguration *cfg = [[WKWebViewConfiguration alloc] init];
    [cfg setURLSchemeHandler:[BundleScheme new] forURLScheme:kScheme];
    WKUserContentController *ucc = [[WKUserContentController alloc] init];
    [ucc addUserScript:[[WKUserScript alloc] initWithSource:[self savedAsScript]
                                              injectionTime:WKUserScriptInjectionTimeAtDocumentStart
                                           forMainFrameOnly:YES]];
    [ucc addScriptMessageHandler:self name:@"hzsave"];
    cfg.userContentController = ucc;
    cfg.allowsInlineMediaPlayback = YES;

    self.web = [[WKWebView alloc] initWithFrame:self.view.bounds configuration:cfg];
    self.web.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
    self.web.opaque = NO;
    self.web.backgroundColor = bg;
    self.web.scrollView.backgroundColor = bg;
    self.web.scrollView.bounces = NO;
    self.web.scrollView.contentInsetAdjustmentBehavior = UIScrollViewContentInsetAdjustmentNever;
    [self.view addSubview:self.web];
    [self.web loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"hzapp://local/index.html"]]];
}

- (void)userContentController:(WKUserContentController *)ucc didReceiveScriptMessage:(WKScriptMessage *)msg {
    if (![msg.body isKindOfClass:[NSDictionary class]]) return;
    NSString *name = msg.body[@"name"];
    NSString *content = msg.body[@"content"];
    if (![name isKindOfClass:[NSString class]] || !SafeName(name)) return;
    NSString *path = [SavesDir() stringByAppendingPathComponent:name];
    if ([msg.body[@"remove"] boolValue]) {
        [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
        return;
    }
    if (![content isKindOfClass:[NSString class]]) return;
    [content writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:nil];
}

- (UIStatusBarStyle)preferredStatusBarStyle { return UIStatusBarStyleLightContent; }
- (BOOL)prefersHomeIndicatorAutoHidden { return YES; }
@end

// ---------------------------------------------------------------- app
@interface AppDelegate : UIResponder <UIApplicationDelegate>
@property (nonatomic, strong) UIWindow *window;
@end

@implementation AppDelegate
- (BOOL)application:(UIApplication *)app didFinishLaunchingWithOptions:(NSDictionary *)opts {
    self.window = [[UIWindow alloc] initWithFrame:[UIScreen mainScreen].bounds];
    self.window.rootViewController = [GameController new];
    [self.window makeKeyAndVisible];
    return YES;
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass([AppDelegate class]));
    }
}
