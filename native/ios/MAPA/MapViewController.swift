import AppTrackingTransparency
import GoogleMobileAds
import UIKit
import UserMessagingPlatform
import WebKit

/* MAP-A in a WKWebView. The page is the same app/index.html the website serves, bundled
   into the app. A banner ad sits below the map. */
final class MapViewController: UIViewController, WKNavigationDelegate, WKUIDelegate {

    private let web: WKWebView = {
        let config = WKWebViewConfiguration()
        config.applicationNameForUserAgent = "MAPA-App/iOS"
        config.allowsInlineMediaPlayback = true
        let view = WKWebView(frame: .zero, configuration: config)
        view.translatesAutoresizingMaskIntoConstraints = false
        view.isOpaque = false
        view.backgroundColor = UIColor(red: 0.196, green: 0.024, blue: 0.067, alpha: 1)
        return view
    }()
    private let adSlot: UIView = {
        let view = UIView()
        view.translatesAutoresizingMaskIntoConstraints = false
        view.backgroundColor = UIColor(red: 0.086, green: 0.047, blue: 0.047, alpha: 1)
        return view
    }()
    private var adHeight: NSLayoutConstraint!
    private var adsStarted = false

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 0.196, green: 0.024, blue: 0.067, alpha: 1)
        view.addSubview(web)
        view.addSubview(adSlot)
        adHeight = adSlot.heightAnchor.constraint(equalToConstant: 0)
        NSLayoutConstraint.activate([
            web.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            web.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            web.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            web.bottomAnchor.constraint(equalTo: adSlot.topAnchor),
            adSlot.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
            adSlot.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor),
            adSlot.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
            adHeight,
        ])
        web.navigationDelegate = self
        web.uiDelegate = self

        if let page = Bundle.main.url(forResource: "index", withExtension: "html") {
            web.loadFileURL(page, allowingReadAccessTo: page.deletingLastPathComponent())
        }
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        gatherConsentThenStartAds()
    }

    /* Google's consent form is shown where the law requires it; then iOS asks before the
       advertising identifier is used. Ads start only once consent allows them. */
    private func gatherConsentThenStartAds() {
        ConsentInformation.shared.requestConsentInfoUpdate(with: RequestParameters()) { [weak self] _ in
            guard let self else { return }
            ConsentForm.loadAndPresentIfRequired(from: self) { [weak self] _ in
                self?.askTrackingThenStartAds()
            }
        }
        if ConsentInformation.shared.canRequestAds { askTrackingThenStartAds() }
    }

    private func askTrackingThenStartAds() {
        guard ConsentInformation.shared.canRequestAds else { return }
        ATTrackingManager.requestTrackingAuthorization { _ in
            DispatchQueue.main.async { self.startAds() }
        }
    }

    private func startAds() {
        guard !adsStarted else { return }
        adsStarted = true
        MobileAds.shared.start(completionHandler: nil)
        let width = view.frame.inset(by: view.safeAreaInsets).width
        let size = currentOrientationAnchoredAdaptiveBanner(width: width)
        let banner = BannerView(adSize: size)
        banner.adUnitID = Bundle.main.object(forInfoDictionaryKey: "ADMOBBannerID") as? String
        banner.rootViewController = self
        banner.translatesAutoresizingMaskIntoConstraints = false
        adSlot.addSubview(banner)
        NSLayoutConstraint.activate([
            banner.centerXAnchor.constraint(equalTo: adSlot.centerXAnchor),
            banner.topAnchor.constraint(equalTo: adSlot.topAnchor),
        ])
        adHeight.constant = size.size.height
        banner.load(Request())
    }

    /* Links that leave the app (phone numbers, websites, map links) open outside it. */
    func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = action.request.url else { return decisionHandler(.allow) }
        if url.isFileURL || url.scheme == "about" || action.targetFrame?.isMainFrame == false {
            return decisionHandler(.allow)
        }
        UIApplication.shared.open(url)
        decisionHandler(.cancel)
    }

    /* target="_blank" and window.open */
    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
                 for action: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = action.request.url { UIApplication.shared.open(url) }
        return nil
    }

    @available(iOS 15.0, *)
    func webView(_ webView: WKWebView, requestMediaCapturePermissionFor origin: WKSecurityOrigin,
                 initiatedByFrame frame: WKFrameInfo, type: WKMediaCaptureType,
                 decisionHandler: @escaping (WKPermissionDecision) -> Void) {
        decisionHandler(.prompt)
    }

    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler() })
        present(alert, animated: true)
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel) { _ in completionHandler(false) })
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler(true) })
        present(alert, animated: true)
    }
}
