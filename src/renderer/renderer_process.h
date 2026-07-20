#ifndef STEALTH_BROWSER_RENDERER_PROCESS_H_
#define STEALTH_BROWSER_RENDERER_PROCESS_H_

#include <string>
#include <vector>

#include "base/memory/ref_counted.h"
#include "content/public/renderer/render_frame_observer.h"

namespace stealth {

class RendererProcess : public content::RenderFrameObserver {
 public:
  explicit RendererProcess(content::RenderFrame* render_frame);
  ~RendererProcess() override;

  void DidFinishLoad() override;
  void DidStartLoading() override;
  void OnNavigationStateChanged() override;

  void InjectFingerprintProtection();
  void InjectSecurityHeaders();
  void NotifyAdBlocker(const std::string& url);

 private:
  void InjectJavaScript(const std::string& script);
  void ApplyContentSecurityPolicy();
  void StripTrackingParameters(std::string* url);

  bool fingerprint_injected_ = false;

  DISALLOW_COPY_AND_ASSIGN(RendererProcess);
};

}  // namespace stealth

#endif  // STEALTH_BROWSER_RENDERER_PROCESS_H_
