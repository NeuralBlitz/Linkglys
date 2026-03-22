package com.neuralblitz.v50.core;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;
import java.util.stream.*;
import java.time.*;
import java.time.format.*;
import java.security.*;
import java.security.spec.*;
import java.security.interfaces.*;
import javax.crypto.*;
import javax.crypto.spec.*;
import javax.crypto.interfaces.*;

public interface AgentConstants {
    long INVALID_ID = 0L;
    double MIN_SCORE = 0.0;
    double MAX_SCORE = 1.0;
    double MIN_TRUST = -1.0;
    double MAX_TRUST = 1.0;
    
    enum AgentState { IDLE, ACTIVE, SUSPENDED, TERMINATED, FAULTED }
    enum TaskState { PENDING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED }
    enum StageState { INITIALIZED, RUNNING, COMPLETED, FAILED, ROLLED_BACK }
    enum GovernanceDecision { APPROVED, DENIED, CONDITIONAL, ESCALATED, DEFERRED }
    enum CapabilityKernel { 
        REASONING(0), PERCEPTION(1), ACTION(2), LEARNING(3), 
        COMMUNICATION(4), PLANNING(5), MONITORING(6), 
        ADAPTATION(7), VERIFICATION(8), GOVERNANCE(9);
        
        private final int code;
        CapabilityKernel(int code) { this.code = code; }
        public int getCode() { return code; }
    }
    
    enum CharterClause {
        PHI_1("Harm Prevention"),
        PHI_2("Value Alignment"),
        PHI_3("Transparency"),
        PHI_4("Fairness"),
        PHI_5("Accountability"),
        PHI_6("Privacy"),
        PHI_7("Security"),
        PHI_8("Human Oversight"),
        PHI_9("Continuous Learning"),
        PHI_10("Robustness"),
        PHI_11("Explainability"),
        PHI_12("Consent"),
        PHI_13("Beneficence"),
        PHI_14("Autonomy"),
        PHI_15("Justice");
        
        private final String description;
        CharterClause(String desc) { this.description = desc; }
        public String getDescription() { return description; }
    }
}

@FunctionalInterface
interface TaskExecutor {
    String execute(Task task);
}

@FunctionalInterface
interface GovernanceEvaluator {
    GovernanceDecision evaluate(Agent agent, Task task);
}

public class UUID {
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();
    
    public static String generate() {
        byte[] bytes = new byte[16];
        SECURE_RANDOM.nextBytes(bytes);
        
        bytes[6] = (byte)((bytes[6] & 0x0f) | 0x40);
        bytes[8] = (byte)((bytes[8] & 0x3f) | 0x80);
        
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 16; i++) {
            if (i == 4 || i == 6 || i == 8 || i == 10) sb.append('-');
            sb.append(String.format("%02x", bytes[i]));
        }
        return sb.toString();
    }
}

public class Crypto static String sha256 {
    public(String input) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(input.getBytes("UTF-8"));
        StringBuilder hexString = new StringBuilder();
        for (byte b : hash) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }
    
    public static String hmacSha256(String key, String message) throws Exception {
        SecretKeySpec secretKey = new SecretKeySpec(key.getBytes("UTF-8"), "HmacSHA256");
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(secretKey);
        byte[] hmacBytes = mac.doFinal(message.getBytes("UTF-8"));
        
        StringBuilder hexString = new StringBuilder();
        for (byte b : hmacBytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }
    
    public static KeyPair generateRsaKeyPair() throws Exception {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
        generator.initialize(2048);
        return generator.generateKeyPair();
    }
    
    public static String sign(String privateKeyPem, String message) throws Exception {
        PrivateKey privateKey = loadPrivateKey(privateKeyPem);
        Signature signer = Signature.getInstance("SHA256withRSA");
        signer.initSign(privateKey);
        signer.update(message.getBytes("UTF-8"));
        byte[] signature = signer.sign();
        return Base64.getEncoder().encodeToString(signature);
    }
    
    public static boolean verify(String publicKeyPem, String message, String signature) throws Exception {
        PublicKey publicKey = loadPublicKey(publicKeyPem);
        Signature verifier = Signature.getInstance("SHA256withRSA");
        verifier.initVerify(publicKey);
        verifier.update(message.getBytes("UTF-8"));
        return verifier.verify(Base64.getDecoder().decode(signature));
    }
    
    private static PrivateKey loadPrivateKey(String pem) throws Exception {
        String lines = pem.replace("-----BEGIN PRIVATE KEY-----", "")
                          .replace("-----END PRIVATE KEY-----", "")
                          .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(lines);
        PKCS8EncodedKeySpec spec = new PKCS8EncodedKeySpec(decoded);
        KeyFactory factory = KeyFactory.getInstance("RSA");
        return factory.generatePrivate(spec);
    }
    
    private static PublicKey loadPublicKey(String pem) throws Exception {
        String lines = pem.replace("-----BEGIN PUBLIC KEY-----", "")
                          .replace("-----END PUBLIC KEY-----", "")
                          .replaceAll("\\s", "");
        byte[] decoded = Base64.getDecoder().decode(lines);
        X509EncodedKeySpec spec = new X509EncodedKeySpec(decoded);
        KeyFactory factory = KeyFactory.getInstance("RSA");
        return factory.generatePublic(spec);
    }
    
    public static String encryptAesGcm(String plaintext, String key) throws Exception {
        byte[] iv = new byte[12];
        SECURE_RANDOM.nextBytes(iv);
        
        SecretKeySpec keySpec = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
        
        byte[] ciphertext = cipher.doFinal(plaintext.getBytes("UTF-8"));
        
        byte[] combined = new byte[iv.length + ciphertext.length];
        System.arraycopy(iv, 0, combined, 0, iv.length);
        System.arraycopy(ciphertext, 0, combined, iv.length, ciphertext.length);
        
        return Base64.getEncoder().encodeToString(combined);
    }
    
    public static String decryptAesGcm(String encrypted, String key) throws Exception {
        byte[] combined = Base64.getDecoder().decode(encrypted);
        
        byte[] iv = new byte[12];
        byte[] ciphertext = new byte[combined.length - 12];
        System.arraycopy(combined, 0, iv, 0, 12);
        System.arraycopy(combined, 12, ciphertext, 0, ciphertext.length);
        
        SecretKeySpec keySpec = new SecretKeySpec(key.getBytes("UTF-8"), "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
        cipher.init(Cipher.DECRYPT_MODE, keySpec, gcmSpec);
        
        byte[] plaintext = cipher.doFinal(ciphertext);
        return new String(plaintext, "UTF-8");
    }
}

public class Logger {
    private static final Logger INSTANCE = new Logger();
    private final List<String> logBuffer = Collections.synchronizedList(new ArrayList<>());
    private Consumer<String> customHandler;
    
    private Logger() {}
    
    public static Logger getInstance() { return INSTANCE; }
    
    public void debug(String message) { log("DEBUG", message); }
    public void info(String message) { log("INFO", message); }
    public void warning(String message) { log("WARN", message); }
    public void error(String message) { log("ERROR", message); }
    
    public void setCustomHandler(Consumer<String> handler) {
        this.customHandler = handler;
    }
    
    private void log(String level, String message) {
        String timestamp = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS")
            .format(LocalDateTime.now());
        String entry = String.format("%s [%s] %s", timestamp, level, message);
        
        logBuffer.add(entry);
        System.out.println(entry);
        
        if (customHandler != null) {
            customHandler.accept(entry);
        }
    }
    
    public List<String> getLogBuffer() { return new ArrayList<>(logBuffer); }
    public void clearBuffer() { logBuffer.clear(); }
}

public class Config {
    private static final Config INSTANCE = new Config();
    private final Map<String, String> config = new ConcurrentHashMap<>();
    
    private Config() {}
    
    public static Config getInstance() { return INSTANCE; }
    
    public void loadFromFile(String path) {
        try {
            Files.lines(Paths.get(path))
                .filter(line -> !line.trim().isEmpty() && !line.startsWith("#"))
                .forEach(line -> {
                    int eqPos = line.indexOf('=');
                    if (eqPos > 0) {
                        String key = line.substring(0, eqPos).trim();
                        String value = line.substring(eqPos + 1).trim();
                        config.put(key, value);
                    }
                });
        } catch (IOException e) {
            Logger.getInstance().warning("Config file not found: " + path);
        }
    }
    
    public String get(String key) { return config.get(key); }
    public String get(String key, String defaultValue) { 
        return config.getOrDefault(key, defaultValue); 
    }
    
    public int getInt(String key, int defaultValue) {
        String value = config.get(key);
        return value != null ? Integer.parseInt(value) : defaultValue;
    }
    
    public double getDouble(String key, double defaultValue) {
        String value = config.get(key);
        return value != null ? Double.parseDouble(value) : defaultValue;
    }
    
    public boolean getBoolean(String key, boolean defaultValue) {
        String value = config.get(key);
        return value != null ? Boolean.parseBoolean(value) : defaultValue;
    }
    
    public void set(String key, String value) { config.put(key, value); }
    public Map<String, String> getAll() { return new HashMap<>(config); }
}
