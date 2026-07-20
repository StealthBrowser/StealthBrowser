#include "src/renderer/renderer_process.h"

#include "base/logging.h"
#include "base/strings/string_util.h"
#include "content/public/renderer/render_frame.h"
#include "third_party/blink/public/common/associated_interfaces/associated_interface_provider.h"
#include "v8/include/v8.h"

namespace stealth {

RendererProcess::RendererProcess(content::RenderFrame* render_frame)
    : content::RenderFrameObserver(render_frame) {}

RendererProcess::~RendererProcess() = default;

void RendererProcess::DidFinishLoad() {
  InjectFingerprintProtection();
  ApplyContentSecurityPolicy();
}

void RendererProcess::DidStartLoading() {
  fingerprint_injected_ = false;
}

void RendererProcess::OnNavigationStateChanged() {
  ApplyContentSecurityPolicy();
}

void RendererProcess::InjectFingerprintProtection() {
  if (fingerprint_injected_ || !render_frame()) {
    return;
  }

  static const char kFingerprintScript[] = R"JS(
    (function() {
      'use strict';

      // Canvas fingerprint protection
      const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
      HTMLCanvasElement.prototype.toDataURL = function(type) {
        const ctx = this.getContext('2d');
        if (ctx) {
          const imageData = ctx.getImageData(0, 0, this.width, this.height);
          for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] = imageData.data[i] ^ (Math.random() > 0.5 ? 1 : 0);
          }
          ctx.putImageData(imageData, 0, 0);
        }
        return origToDataURL.apply(this, arguments);
      };

      // WebGL fingerprint protection
      const getParameter = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function(param) {
        const ext = this.getExtension('WEBGL_debug_renderer_info');
        if (ext && param === ext.UNMASKED_VENDOR_WEBGL) return 'Intel Inc.';
        if (ext && param === ext.UNMASKED_RENDERER_WEBGL) return 'Intel Iris OpenGL Engine';
        return getParameter.call(this, param);
      };

      // AudioContext fingerprint protection
      const origGetChannelData = AudioBuffer.prototype.getChannelData;
      AudioBuffer.prototype.getChannelData = function(channel) {
        const data = origGetChannelData.call(this, channel);
        for (let i = 0; i < data.length; i++) {
          data[i] += Math.random() * 0.0001;
        }
        return data;
      };

      // Navigator protection
      Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
      Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
      Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

      // Screen protection
      Object.defineProperty(screen, 'width', { get: () => 1920 });
      Object.defineProperty(screen, 'height', { get: () => 1080 });
    })();
  )JS";

  InjectJavaScript(kFingerprintScript);
  fingerprint_injected_ = true;
}

void RendererProcess::InjectSecurityHeaders() {
  static const char kSecurityScript[] = R"JS(
    (function() {
      'use strict';
      Object.defineProperty(navigator, 'doNotTrack', { get: () => '1' });
      Object.defineProperty(navigator, 'cookieEnabled', { get: () => false });
    })();
  )JS";

  InjectJavaScript(kSecurityScript);
}

void RendererProcess::NotifyAdBlocker(const std::string& url) {
  // Notify the ad blocker about the navigation
  // This is called from the renderer to inform the browser process
}

void RendererProcess::InjectJavaScript(const std::string& script) {
  if (!render_frame()) {
    return;
  }

  v8::Isolate* isolate = v8::Isolate::GetCurrent();
  if (!isolate) {
    return;
  }

  v8::HandleScope handle_scope(isolate);
  v8::Local<v8::Context> context = render_frame()->GetWebFrame()->GetMainWorldScriptContext();
  if (context.IsEmpty()) {
    return;
  }

  v8::Context::Scope context_scope(context);
  v8::Local<v8::Script> v8_script = v8::Script::Compile(
      context,
      v8::String::NewFromUtf8(isolate, script.c_str()).ToLocalChecked())
      .ToLocalChecked();

  v8_script->Run(context).FromMaybe(v8::Local<v8::Value>());
}

void RendererProcess::ApplyContentSecurityPolicy() {
  InjectSecurityHeaders();
}

void RendererProcess::StripTrackingParameters(std::string* url) {
  static const std::vector<std::string> kTrackingParams = {
      "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
      "fbclid", "gclid", "dclid", "msclkid", "twclid",
      "li_fat_id", "_openstat", "yclid",
  };

  for (const auto& param : kTrackingParams) {
    size_t pos = url->find(param);
    if (pos != std::string::npos) {
      size_t start = url->rfind('?', pos);
      if (start == std::string::npos) {
        start = url->rfind('&', pos);
      }
      if (start != std::string::npos) {
        size_t end = url->find('&', pos);
        if (end == std::string::npos) {
          end = url->length();
        } else {
          end++;
        }
        url->erase(start, end - start);
      }
    }
  }
}

}  // namespace stealth
