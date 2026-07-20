#ifndef STEALTH_BROWSER_BROWSER_PROCESS_H_
#define STEALTH_BROWSER_BROWSER_PROCESS_H_

#include <memory>
#include <string>
#include <vector>

#include "base/memory/ref_counted.h"
#include "base/task/sequenced_task_runner.h"
#include "content/public/browser/browser_process.h"

namespace stealth {

class SecurityManager;
class AdBlockerBridge;

struct BrowserConfig {
  std::string user_agent;
  bool enable_https_only = true;
  bool enable_fingerprint_protection = true;
  bool enable_ad_blocking = true;
  bool clear_data_on_exit = true;
  std::string cache_path;
  std::string data_path;
};

class BrowserProcess : public base::RefCountedThreadSafe<BrowserProcess> {
 public:
  static BrowserProcess* GetInstance();

  bool Initialize(const BrowserConfig& config);
  void Shutdown();

  SecurityManager* security_manager() const { return security_manager_.get(); }
  AdBlockerBridge* adblocker() const { return adblocker_.get(); }

  const BrowserConfig& config() const { return config_; }

 private:
  BrowserProcess();
  ~BrowserProcess() override;

  friend class base::RefCountedThreadSafe<BrowserProcess>;

  BrowserConfig config_;
  std::unique_ptr<SecurityManager> security_manager_;
  std::unique_ptr<AdBlockerBridge> adblocker_;

  DISALLOW_COPY_AND_ASSIGN(BrowserProcess);
};

}  // namespace stealth

#endif  // STEALTH_BROWSER_BROWSER_PROCESS_H_
