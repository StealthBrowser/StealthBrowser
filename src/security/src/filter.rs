use std::collections::HashSet;
use std::sync::RwLock;

use regex::Regex;
use url::Url;

pub struct FilterEngine {
    domain_filters: RwLock<HashSet<String>>,
    pattern_filters: RwLock<Vec<Regex>>,
    keyword_filters: RwLock<HashSet<String>>,
    allowed_domains: RwLock<HashSet<String>>,
}

impl FilterEngine {
    pub fn new() -> Self {
        let mut engine = Self {
            domain_filters: RwLock::new(HashSet::new()),
            pattern_filters: RwLock::new(Vec::new()),
            keyword_filters: RwLock::new(HashSet::new()),
            allowed_domains: RwLock::new(HashSet::new()),
        };
        engine.load_default_filters();
        engine
    }

    fn load_default_filters(&mut self) {
        let tracker_domains = vec![
            "google-analytics.com", "googletagmanager.com",
            "googlesyndication.com", "googleadservices.com",
            "doubleclick.net", "facebook.com", "facebook.net",
            "analytics.twitter.com", "ads-twitter.com",
            "ads.linkedin.com", "bat.bing.com",
            "hotjar.com", "heap.io", "mixpanel.com",
            "segment.io", "amplitude.com", "branch.io",
            "adjust.com", "appsflyer.com", "sentry.io",
            "bugsnag.com", "newrelic.com", "datadoghq.com",
            "chartbeat.com", "quantserve.com",
            "scorecardresearch.com", "bluekai.com",
            "rubiconproject.com", "pubmatic.com", "openx.net",
            "criteo.com", "criteo.net", "taboola.com",
            "outbrain.com", "moat.com", "integralads.com",
            "doubleverify.com", "permutive.com", "liveramp.com",
            "demdex.net", "adnxs.com", "bidswitch.net",
        ];

        for domain in tracker_domains {
            self.domain_filters.write().unwrap().insert(domain.to_string());
        }
    }

    pub fn should_block(&self, url: &str) -> bool {
        let parsed = match Url::parse(url) {
            Ok(u) => u,
            Err(_) => return false,
        };

        let hostname = match parsed.host_str() {
            Some(h) => h,
            None => return false,
        };

        // Check domain filters
        let domains = self.domain_filters.read().unwrap();
        for domain in domains.iter() {
            if hostname == domain || hostname.ends_with(&format!(".{}", domain)) {
                return true;
            }
        }

        // Check keyword filters
        let keywords = self.keyword_filters.read().unwrap();
        for keyword in keywords.iter() {
            if url.contains(keyword.as_str()) {
                return true;
            }
        }

        // Check pattern filters
        let patterns = self.pattern_filters.read().unwrap();
        for pattern in patterns.iter() {
            if pattern.is_match(url) {
                return true;
            }
        }

        false
    }

    pub fn should_upgrade_to_https(&self, url: &str) -> bool {
        if url.starts_with("https://") {
            return false;
        }

        if let Ok(parsed) = Url::parse(url) {
            if let Some(host) = parsed.host_str() {
                let exceptions = self.allowed_domains.read().unwrap();
                if exceptions.contains(host) {
                    return false;
                }
            }
        }

        url.starts_with("http://")
    }

    pub fn add_domain_filter(&self, domain: String) {
        self.domain_filters.write().unwrap().insert(domain);
    }

    pub fn remove_domain_filter(&self, domain: &str) {
        self.domain_filters.write().unwrap().remove(domain);
    }

    pub fn add_pattern_filter(&self, pattern: &str) -> Result<(), String> {
        let re = Regex::new(pattern)
            .map_err(|e| format!("Invalid regex: {}", e))?;
        self.pattern_filters.write().unwrap().push(re);
        Ok(())
    }

    pub fn add_keyword_filter(&self, keyword: String) {
        self.keyword_filters.write().unwrap().insert(keyword);
    }

    pub fn add_allowed_domain(&self, domain: String) {
        self.allowed_domains.write().unwrap().insert(domain);
    }

    pub fn get_stats(&self) -> FilterStats {
        FilterStats {
            domain_filters: self.domain_filters.read().unwrap().len(),
            pattern_filters: self.pattern_filters.read().unwrap().len(),
            keyword_filters: self.keyword_filters.read().unwrap().len(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct FilterStats {
    pub domain_filters: usize,
    pub pattern_filters: usize,
    pub keyword_filters: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_block_tracker() {
        let engine = FilterEngine::new();
        assert!(engine.should_block("https://google-analytics.com/track"));
        assert!(engine.should_block("https://www.facebook.com/tr/123"));
        assert!(!engine.should_block("https://github.com/user/repo"));
    }

    #[test]
    fn test_https_upgrade() {
        let engine = FilterEngine::new();
        assert!(engine.should_upgrade_to_https("http://example.com"));
        assert!(!engine.should_upgrade_to_https("https://example.com"));
        assert!(!engine.should_upgrade_to_https("http://localhost"));
    }
}
