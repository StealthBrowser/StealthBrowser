#include "src/browser/browser_process.h"

#include "base/logging.h"
#include "base/files/file_path.h"
#include "base/task/thread_pool.h"
#include "src/security/security_binding.h"

namespace stealth {

BrowserProcess::BrowserProcess() = default;
BrowserProcess::~BrowserProcess() = default;

BrowserProcess* BrowserProcess::GetInstance() {
  static base::NoDestructor<BrowserProcess> instance;
  return instance.get();
}

bool BrowserProcess::Initialize(const BrowserConfig& config) {
  config_ = config;
  LOG(INFO) << "StealthBrowser: Initializing browser process";

  security_manager_ = std::make_unique<SecurityManager>();
  if (!security_manager_->Initialize(config)) {
    LOG(ERROR) << "StealthBrowser: Failed to initialize security manager";
    return false;
  }

  if (config.enable_ad_blocking) {
    adblocker_ = std::make_unique<AdBlockerBridge>();
    if (!adblocker_->Initialize()) {
      LOG(WARNING) << "StealthBrowser: Failed to initialize ad blocker";
    }
  }

  LOG(INFO) << "StealthBrowser: Browser process initialized";
  return true;
}

void BrowserProcess::Shutdown() {
  LOG(INFO) << "StealthBrowser: Shutting down browser process";

  if (config_.clear_data_on_exit) {
    security_manager_->ClearAllData();
  }

  adblocker_.reset();
  security_manager_.reset();

  LOG(INFO) << "StealthBrowser: Shutdown complete";
}

}  // namespace stealth
