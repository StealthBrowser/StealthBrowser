#ifndef STEALTH_SECURITY_SECURITY_BINDING_H_
#define STEALTH_SECURITY_SECURITY_BINDING_H_

#include <cstdint>
#include <string>

#ifdef __cplusplus
extern "C" {
#endif

int stealth_security_init(void);
int stealth_should_block_url(const char* url);
int stealth_should_upgrade_https(const char* url);
uint64_t stealth_get_blocked_count(void);
int stealth_clear_session(void);
int stealth_add_block_domain(const char* domain);
int stealth_security_shutdown(void);

#ifdef __cplusplus
}
#endif

namespace stealth {

class SecurityBinding {
 public:
  static SecurityBinding& GetInstance();

  bool Initialize();
  void Shutdown();

  bool ShouldBlockURL(const std::string& url) const;
  bool ShouldUpgradeHTTPS(const std::string& url) const;
  uint64_t GetBlockedCount() const;
  void ClearSession();
  bool AddBlockDomain(const std::string& domain);

 private:
  SecurityBinding() = default;
  ~SecurityBinding() = default;

  bool initialized_ = false;
};

}  // namespace stealth

#endif  // STEALTH_SECURITY_SECURITY_BINDING_H_
