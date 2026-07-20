use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use base64::{engine::general_purpose::STANDARD as B64, Engine};
use rand::Rng;
use sha2::{Digest, Sha256};

pub struct CryptoEngine {
    cipher: Aes256Gcm,
}

impl CryptoEngine {
    pub fn new(key: &[u8; 32]) -> Self {
        let cipher = Aes256Gcm::new_from_slice(key)
            .expect("Invalid key length");
        Self { cipher }
    }

    pub fn generate_key() -> [u8; 32] {
        let mut key = [0u8; 32];
        rand::thread_rng().fill(&mut key);
        key
    }

    pub fn encrypt(&self, plaintext: &[u8]) -> Result<String, String> {
        let mut nonce_bytes = [0u8; 12];
        rand::thread_rng().fill(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self.cipher
            .encrypt(nonce, plaintext)
            .map_err(|e| format!("Encryption failed: {}", e))?;

        let mut output = nonce_bytes.to_vec();
        output.extend(ciphertext);
        Ok(B64.encode(&output))
    }

    pub fn decrypt(&self, encoded: &str) -> Result<Vec<u8>, String> {
        let data = B64.decode(encoded)
            .map_err(|e| format!("Base64 decode failed: {}", e))?;

        if data.len() < 12 {
            return Err("Invalid ciphertext".to_string());
        }

        let nonce = Nonce::from_slice(&data[..12]);
        let ciphertext = &data[12..];

        self.cipher
            .decrypt(nonce, ciphertext)
            .map_err(|e| format!("Decryption failed: {}", e))
    }

    pub fn hash(data: &[u8]) -> [u8; 32] {
        let mut hasher = Sha256::new();
        hasher.update(data);
        hasher.finalize().into()
    }

    pub fn hash_string(input: &str) -> String {
        let hash = Self::hash(input.as_bytes());
        hex::encode(hash)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encrypt_decrypt() {
        let key = CryptoEngine::generate_key();
        let engine = CryptoEngine::new(&key);
        let plaintext = b"Hello, World!";
        let encrypted = engine.encrypt(plaintext).unwrap();
        let decrypted = engine.decrypt(&encrypted).unwrap();
        assert_eq!(plaintext.to_vec(), decrypted);
    }

    #[test]
    fn test_hash() {
        let hash = CryptoEngine::hash(b"test");
        assert_eq!(hash.len(), 32);
    }
}
