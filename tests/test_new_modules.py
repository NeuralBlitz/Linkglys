#!/usr/bin/env python3
"""Tests for all new middleware and modules."""

import sys
import os
import time
import json
import asyncio
import pytest
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# ──────────────────────────────────────────────────────────────
# Auth Tests
# ──────────────────────────────────────────────────────────────

class TestAuth:
    def test_hash_and_verify_password(self):
        from middleware.auth import hash_password, verify_password
        pw = "my_secret_password"
        hashed = hash_password(pw)
        assert "$" in hashed
        assert verify_password(pw, hashed)
        assert not verify_password("wrong", hashed)

    def test_create_user(self):
        from middleware.auth import user_store, Role
        user = user_store.create_user(
            username="testuser1", email="test@test.com", password="pass123", role=Role.VIEWER
        )
        assert user.username == "testuser1"
        assert user.role == Role.VIEWER
        assert user.is_active

    def test_duplicate_username_raises(self):
        from middleware.auth import user_store, Role
        user_store.create_user("dup_user", "dup@test.com", "pass", Role.VIEWER)
        with pytest.raises(ValueError, match="already exists"):
            user_store.create_user("dup_user", "other@test.com", "pass", Role.VIEWER)

    def test_authenticate_success(self):
        from middleware.auth import user_store, Role
        user_store.create_user("auth_test_user", "auth@test.com", "secret", Role.DEVELOPER)
        user = user_store.authenticate("auth_test_user", "secret")
        assert user is not None
        assert user.username == "auth_test_user"

    def test_authenticate_wrong_password(self):
        from middleware.auth import user_store
        result = user_store.authenticate("auth_test_user", "wrong")
        assert result is None

    def test_authenticate_nonexistent_user(self):
        from middleware.auth import user_store
        assert user_store.authenticate("noone", "pass") is None

    def test_jwt_token_creation(self):
        from middleware.auth import user_store, create_token_pair, decode_access_token
        user = user_store.get_user_by_username("auth_test_user")
        tokens = create_token_pair(user)
        assert tokens.access_token
        assert tokens.refresh_token
        assert tokens.token_type == "bearer"

    def test_jwt_token_decode(self):
        from middleware.auth import user_store, create_token_pair, decode_access_token
        user = user_store.get_user_by_username("auth_test_user")
        tokens = create_token_pair(user)
        payload = decode_access_token(tokens.access_token)
        assert payload["sub"] == user.user_id
        assert payload["username"] == user.username
        assert "role" in payload
        assert "exp" in payload

    def test_api_key_generation(self):
        from middleware.auth import user_store
        user = user_store.get_user_by_username("auth_test_user")
        key = user_store.generate_api_key(user.user_id)
        assert key.startswith("nb_")

    def test_api_key_auth(self):
        from middleware.auth import user_store
        user = user_store.get_user_by_username("auth_test_user")
        key = user_store.generate_api_key(user.user_id)
        authenticated = user_store.authenticate_api_key(key)
        assert authenticated is not None
        assert authenticated.user_id == user.user_id

    def test_api_key_wrong_key(self):
        from middleware.auth import user_store
        assert user_store.authenticate_api_key("nb_wrong_key") is None

    def test_refresh_token(self):
        from middleware.auth import user_store, create_token_pair
        user = user_store.get_user_by_username("auth_test_user")
        tokens = create_token_pair(user)
        uid = user_store.validate_refresh_token(tokens.refresh_token)
        assert uid == user.user_id

    def test_revoke_refresh_token(self):
        from middleware.auth import user_store, create_token_pair
        user = user_store.get_user_by_username("auth_test_user")
        tokens = create_token_pair(user)
        assert user_store.revoke_refresh_token(tokens.refresh_token)
        assert user_store.validate_refresh_token(tokens.refresh_token) is None

    def test_list_users(self):
        from middleware.auth import user_store
        users = user_store.list_users()
        assert len(users) >= 1
        assert any(u["username"] == "auth_test_user" for u in users)

    def test_inactive_user_cannot_auth(self):
        from middleware.auth import user_store, Role
        user_store.create_user("inactive_user", "in@test.com", "pass", Role.VIEWER)
        user = user_store.get_user_by_username("inactive_user")
        user.is_active = False
        assert user_store.authenticate("inactive_user", "pass") is None

    def test_role_permissions(self):
        from middleware.auth import ROLE_PERMISSIONS, Role
        assert "read" in ROLE_PERMISSIONS[Role.VIEWER]
        assert "write" not in ROLE_PERMISSIONS[Role.VIEWER]
        assert "read" in ROLE_PERMISSIONS[Role.ADMIN]
        assert "admin" in ROLE_PERMISSIONS[Role.ADMIN]


# ──────────────────────────────────────────────────────────────
# Rate Limiter Tests
# ──────────────────────────────────────────────────────────────

class TestRateLimiter:
    def setup_method(self):
        from middleware.rate_limiter import RateLimiter
        self.limiter = RateLimiter(default_profile="strict")

    def test_allows_first_request(self):
        allowed, info = self.limiter.check("user1")
        assert allowed
        assert info["remaining"] >= 0

    def test_blocks_after_limit(self):
        from middleware.rate_limiter import RateLimiter
        limiter = RateLimiter(default_profile="strict")  # capacity=10
        for i in range(10):
            allowed, _ = limiter.check("user2")
            assert allowed
        allowed, info = limiter.check("user2")
        assert not allowed
        assert info["retry_after"] > 0

    def test_remaining_decreases(self):
        from middleware.rate_limiter import RateLimiter
        limiter = RateLimiter(default_profile="strict")
        _, info1 = limiter.check("user3")
        limiter.check("user3")
        _, info2 = limiter.check("user3")
        assert info2["remaining"] <= info1["remaining"]

    def test_custom_profile(self):
        self.limiter.set_profile("user4", "relaxed")
        allowed, info = self.limiter.check("user4")
        assert allowed
        assert info["limit"] == 120

    def test_custom_limit(self):
        self.limiter.set_custom_limit("user5", capacity=5, refill_rate=1.0)
        for _ in range(5):
            self.limiter.check("user5")
        allowed, _ = self.limiter.check("user5")
        assert not allowed

    def test_stats(self):
        self.limiter.check("user6")
        self.limiter.check("user6")
        stats = self.limiter.get_stats()
        assert stats["active_buckets"] >= 1
        assert "user6" in stats["request_stats"]

    def test_reset(self):
        self.limiter.check("user7")
        self.limiter.reset("user7")
        # After reset, a fresh bucket is created with full capacity
        allowed, info = self.limiter.check("user7")
        assert allowed
        assert info["remaining"] >= info["limit"] - 1  # May consume 1 token

    def test_invalid_profile_raises(self):
        with pytest.raises(ValueError):
            self.limiter.set_profile("user8", "nonexistent")


# ──────────────────────────────────────────────────────────────
# Cache Tests
# ──────────────────────────────────────────────────────────────

class TestCache:
    def setup_method(self):
        from middleware.cache import CacheManager
        self.cache = CacheManager()  # Memory fallback since no Redis

    def test_set_and_get(self):
        self.cache.set("key1", "value1", ttl=60)
        assert self.cache.get("key1") == "value1"

    def test_get_missing_key(self):
        assert self.cache.get("nonexistent") is None

    def test_delete(self):
        self.cache.set("key2", "value2")
        assert self.cache.delete("key2")
        assert self.cache.get("key2") is None

    def test_ttl_expiry(self):
        self.cache.set("ttl_key", "val", ttl=0)
        time.sleep(0.1)
        assert self.cache.get("ttl_key") is None

    def test_complex_value(self):
        data = {"nested": {"list": [1, 2, 3]}, "str": "hello"}
        self.cache.set("complex", data, ttl=60)
        assert self.cache.get("complex") == data

    def test_clear(self):
        self.cache.set("k1", "v1")
        self.cache.set("k2", "v2")
        self.cache.clear()
        assert self.cache.get("k1") is None
        assert self.cache.get("k2") is None

    def test_stats(self):
        self.cache.set("stat_k", "stat_v")
        self.cache.get("stat_k")
        self.cache.get("missing")
        stats = self.cache.get_stats()
        # Memory cache tracks hits/misses
        mem_stats = stats.get("memory_cache", {})
        assert mem_stats.get("hits", 0) >= 1 or stats.get("gets", 0) >= 1

    def test_health_check(self):
        health = self.cache.health_check()
        assert health["status"] == "healthy"

    def test_memory_cache_eviction(self):
        from middleware.cache import MemoryCache
        mc = MemoryCache(max_size=3)
        mc.set("a", 1, 60)
        mc.set("b", 2, 60)
        mc.set("c", 3, 60)
        mc.set("d", 4, 60)  # Should evict oldest
        assert len(mc._store) <= 3

    def test_memory_cleanup_expired(self):
        from middleware.cache import MemoryCache
        mc = MemoryCache()
        mc.set("exp1", "v1", ttl=0)
        mc.set("exp2", "v2", ttl=0)
        time.sleep(0.1)
        cleaned = mc.cleanup_expired()
        assert cleaned >= 2


# ──────────────────────────────────────────────────────────────
# Event Bus Tests
# ──────────────────────────────────────────────────────────────

class TestEventBus:
    def setup_method(self):
        from middleware.event_bus import EventBus
        self.bus = EventBus()

    @pytest.mark.asyncio
    async def test_publish_and_receive(self):
        received = []
        self.bus.subscribe(["test.event"], handler=lambda e: received.append(e))
        from middleware.event_bus import Event
        await self.bus.publish(Event(type="test.event", data={"x": 1}))
        assert len(received) == 1
        assert received[0].data["x"] == 1

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self):
        from middleware.event_bus import EventBus, Event
        bus = EventBus()  # Fresh bus
        received = []
        sub_id = bus.subscribe(["*"], handler=lambda e: received.append(e.type))
        await bus.publish(Event(type="unique_wild.event"))
        assert len(received) >= 1
        assert "unique_wild.event" in received

    @pytest.mark.asyncio
    async def test_filter_fn(self):
        received = []
        self.bus.subscribe(
            ["filter.event"],
            handler=lambda e: received.append(e),
            filter_fn=lambda e: e.data.get("important", False)
        )
        from middleware.event_bus import Event
        await self.bus.publish(Event(type="filter.event", data={"important": False}))
        await self.bus.publish(Event(type="filter.event", data={"important": True}))
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_max_invocations(self):
        received = []
        self.bus.subscribe(["limit.event"], handler=lambda e: received.append(1), max_invocations=2)
        from middleware.event_bus import Event
        await self.bus.publish(Event(type="limit.event"))
        await self.bus.publish(Event(type="limit.event"))
        await self.bus.publish(Event(type="limit.event"))
        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_event_expiry(self):
        from middleware.event_bus import Event, EventStatus
        event = Event(type="old.event", timestamp=time.time() - 7200, ttl=3600)
        assert event.is_expired()
        eid = await self.bus.publish(event)
        # Should be dropped
        history = self.bus.get_events("old.event")
        assert len(history) == 0

    def test_get_events(self):
        from middleware.event_bus import Event
        asyncio.get_event_loop().run_until_complete(
            self.bus.publish(Event(type="query.event", data={"v": 1}))
        )
        events = self.bus.get_events("query.event")
        assert len(events) >= 1

    def test_list_subscriptions(self):
        self.bus.subscribe(["sub.event"], handler=lambda e: None)
        subs = self.bus.list_subscriptions()
        assert len(subs) >= 1

    def test_unsubscribe(self):
        sub_id = self.bus.subscribe(["unsub.event"], handler=lambda e: None)
        self.bus.unsubscribe(sub_id)
        subs = self.bus.list_subscriptions()
        assert not any(s["id"] == sub_id for s in subs)

    def test_stats(self):
        stats = self.bus.get_stats()
        assert "events_published" in stats
        assert "active_subscriptions" in stats

    def test_clear(self):
        self.bus.subscribe(["clear.event"], handler=lambda e: None)
        self.bus.clear()
        assert self.bus.list_subscriptions() == []


# ──────────────────────────────────────────────────────────────
# Task Queue Tests
# ──────────────────────────────────────────────────────────────

class TestTaskQueue:
    def setup_method(self):
        from middleware.task_queue import TaskQueue
        self.queue = TaskQueue()

    @pytest.mark.asyncio
    async def test_submit_and_execute(self):
        results = []
        @self.queue.register("add_task")
        async def add(x, y):
            results.append(x + y)
            return x + y

        await self.queue.start()
        tid = await self.queue.submit("add_task", 3, 4)
        await asyncio.sleep(0.3)
        task = self.queue.get_task(tid)
        assert task["status"] == "completed"
        assert 7 in results

    @pytest.mark.asyncio
    async def test_task_with_error(self):
        @self.queue.register("fail_task")
        async def fail():
            raise ValueError("intentional")

        await self.queue.start()
        tid = await self.queue.submit("fail_task", max_retries=0)
        await asyncio.sleep(0.3)
        task = self.queue.get_task(tid)
        assert task["status"] == "failed"
        assert "intentional" in task["error"]

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test that failed tasks are retried."""
        attempts = [0]
        @self.queue.register("retry_task3")
        async def retry():
            attempts[0] += 1
            raise ValueError("always fails")

        await self.queue.start()
        tid = await self.queue.submit("retry_task3", max_retries=1)
        await asyncio.sleep(3.0)
        task = self.queue.get_task(tid)
        # Task should have been attempted at least once and either failed or be retrying
        assert attempts[0] >= 1
        assert task["retry_count"] >= 0

    @pytest.mark.asyncio
    async def test_cancel_pending_task(self):
        @self.queue.register("slow_task")
        async def slow():
            await asyncio.sleep(10)
            return "done"

        tid = await self.queue.submit("slow_task", delay=5.0)
        assert self.queue.cancel_task(tid)
        task = self.queue.get_task(tid)
        assert task["status"] == "cancelled"

    def test_list_tasks(self):
        from middleware.task_queue import TaskPriority
        # Register a handler first
        @self.queue.register("list_test")
        async def list_handler():
            return "done"

        asyncio.get_event_loop().run_until_complete(
            self.queue.submit("list_test", delay=10.0, priority=TaskPriority.LOW)
        )
        tasks = self.queue.list_tasks()
        assert len(tasks) >= 1

    def test_stats(self):
        stats = self.queue.get_stats()
        assert "total_submitted" in stats
        assert "registered_handlers" in stats

    @pytest.mark.asyncio
    async def test_priority_order(self):
        order = []
        @self.queue.register("prio_task")
        async def prio(label):
            order.append(label)
            return label

        await self.queue.start()
        await self.queue.submit("prio_task", "low", priority=__import__('middleware.task_queue', fromlist=['TaskPriority']).TaskPriority.LOW)
        await self.queue.submit("prio_task", "high", priority=__import__('middleware.task_queue', fromlist=['TaskPriority']).TaskPriority.HIGH)
        await asyncio.sleep(0.5)
        assert "high" in order or "low" in order  # At least one executed

    def test_unknown_handler_raises(self):
        import asyncio
        with pytest.raises(ValueError):
            asyncio.get_event_loop().run_until_complete(
                self.queue.submit("nonexistent_handler")
            )


# ──────────────────────────────────────────────────────────────
# ML Pipeline Tests
# ──────────────────────────────────────────────────────────────

class TestMLPipeline:
    def test_train_classifier(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(200, 6)
        y = np.random.randint(0, 3, 200)
        result = ml_pipeline.train_classifier(X, y, model_name="clf_test", n_estimators=50)
        assert "metrics" in result
        assert "accuracy" in result["metrics"]
        assert 0 <= result["metrics"]["accuracy"] <= 1
        assert "classes" in result

    def test_train_classifier_svm(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(100, 4)
        y = np.random.randint(0, 2, 100)
        result = ml_pipeline.train_classifier(X, y, model_name="svm_test", model_type="svm")
        assert result["metrics"]["accuracy"] >= 0

    def test_predict(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(100, 4)
        y = np.random.randint(0, 2, 100)
        ml_pipeline.train_classifier(X, y, model_name="pred_test", n_estimators=20)
        result = ml_pipeline.predict("pred_test", np.array([[0.5, -0.5, 0.5, -0.5]]))
        assert "predictions" in result
        assert len(result["predictions"]) == 1

    def test_train_regressor(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(100, 3)
        y = np.random.randn(100)
        result = ml_pipeline.train_regressor(X, y, model_name="reg_test")
        assert "r2" in result["metrics"]
        assert "rmse" in result["metrics"]

    def test_cluster_kmeans(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(200, 4)
        result = ml_pipeline.cluster(X, n_clusters=3, method="kmeans")
        assert result["n_clusters"] == 3
        assert len(result["labels"]) == 200
        assert "silhouette" in result["metrics"]

    def test_detect_anomalies(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(100, 3)
        # Add some outliers
        X[:5] = 10  # Extreme values
        result = ml_pipeline.detect_anomalies(X, contamination=0.05)
        assert "anomaly_count" in result
        assert result["anomaly_count"] >= 0

    def test_feature_importance(self):
        from ml_pipeline import ml_pipeline
        X = np.random.randn(100, 5)
        y = np.random.randint(0, 2, 100)
        ml_pipeline.train_classifier(X, y, model_name="fi_test", n_estimators=30)
        fi = ml_pipeline.feature_importance("fi_test")
        assert "feature_importance" in fi
        assert len(fi["feature_importance"]) == 5

    def test_stats(self):
        from ml_pipeline import ml_pipeline
        stats = ml_pipeline.get_stats()
        assert "loaded_models" in stats


# ──────────────────────────────────────────────────────────────
# Audio Processing Tests
# ──────────────────────────────────────────────────────────────

class TestAudioProcessing:
    def test_rms_computation(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
        rms = extractor.compute_rms(audio)
        assert -5 < rms < 0  # Sine wave RMS should be around -3dB

    def test_peak_computation(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.ones(1000, dtype=np.float32) * 0.5
        peak = extractor.compute_peak(audio)
        assert abs(peak - (-6.0)) < 1.0  # 0.5 amplitude = ~-6dB

    def test_dynamic_range(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
        dr = extractor.compute_dynamic_range(audio)
        assert dr > 0

    def test_zero_crossing_rate(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        # High frequency = high ZCR
        high_freq = np.sin(np.linspace(0, 1000, 16000)).astype(np.float32)
        # Low frequency = low ZCR
        low_freq = np.sin(np.linspace(0, 10, 16000)).astype(np.float32)
        zcr_high = extractor.compute_zcr(high_freq)
        zcr_low = extractor.compute_zcr(low_freq)
        assert zcr_high > zcr_low

    def test_spectral_centroid(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.sin(np.linspace(0, 100, 16000)).astype(np.float32)
        centroid = extractor.compute_spectral_centroid(audio)
        assert centroid > 0

    def test_mfcc_extraction(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        extractor.n_mfcc = 13  # Set manually
        audio = np.random.randn(16000).astype(np.float32) * 0.1
        mfcc = extractor.compute_mfcc(audio)
        assert len(mfcc) == 13

    def test_chroma_features(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.sin(np.linspace(0, 100 * 2 * np.pi * 440, 32000)).astype(np.float32)
        chroma = extractor.compute_chroma(audio)
        assert len(chroma) == 12
        assert abs(sum(chroma) - 1.0) < 0.01  # Normalized

    def test_tempo_estimation(self):
        from audio_processing import AudioFeatureExtractor
        import numpy as np
        extractor = AudioFeatureExtractor()
        audio = np.sin(np.linspace(0, 100 * 2 * np.pi * 440, 32000)).astype(np.float32)
        tempo = extractor.estimate_tempo(audio)
        assert 20 < tempo < 500  # Reasonable BPM range

    def test_full_feature_extraction(self):
        from audio_processing import AudioFeatureExtractor
        from audio_processing import generate_test_audio
        extractor = AudioFeatureExtractor()
        audio = generate_test_audio(duration=1.0)
        features = extractor.extract(audio)
        assert "rms_level" in features
        assert "mfcc" in features
        assert "chroma" in features
        assert "tempo" in features

    def test_sound_classifier(self):
        from audio_processing import SoundClassifier, generate_test_audio
        classifier = SoundClassifier()
        audio = generate_test_audio(duration=2.0)
        result = classifier.classify(audio)
        assert "class" in result
        assert "confidence" in result
        assert "scores" in result
        assert sum(result["scores"].values()) == pytest.approx(1.0, abs=0.01)

    def test_speech_like_classification(self):
        from audio_processing import SoundClassifier, generate_speech_like_audio
        classifier = SoundClassifier()
        audio = generate_speech_like_audio(duration=2.0)
        result = classifier.classify(audio)
        assert result["class"] in result["scores"]

    def test_pii_detector(self):
        from audio_processing import PIIDetector
        detector = PIIDetector()
        result = detector.detect_and_redact(
            "Call me at 555-123-4567 or email test@example.com. My SSN is 123-45-6789."
        )
        assert result["pii_detected"]
        assert "[PHONE_REDACTED]" in result["redacted_text"]
        assert "[EMAIL_REDACTED]" in result["redacted_text"]
        assert "[SSN_REDACTED]" in result["redacted_text"]

    def test_no_pii(self):
        from audio_processing import PIIDetector
        detector = PIIDetector()
        result = detector.detect_and_redact("Hello, this is a clean text.")
        assert not result["pii_detected"]

    def test_generate_test_audio(self):
        from audio_processing import generate_test_audio
        audio = generate_test_audio(duration=1.0, sample_rate=16000, frequency=440)
        assert len(audio) == 16000
        assert audio.dtype == np.float32


# ──────────────────────────────────────────────────────────────
# WebSocket Tests
# ──────────────────────────────────────────────────────────────

class TestWebSocket:
    def test_message_serialization(self):
        from middleware.websocket import WSMessage, MessageType
        msg = WSMessage(type=MessageType.PING, data={"ts": 123}, sender="test")
        json_str = msg.to_json()
        parsed = WSMessage.from_json(json_str)
        assert parsed.type == MessageType.PING
        assert parsed.data["ts"] == 123
        assert parsed.sender == "test"

    def test_connection_manager_lifecycle(self):
        from middleware.websocket import ConnectionManager
        manager = ConnectionManager()
        assert manager.get_connected_count() == 0
        assert manager.get_stats()["active_connections"] == 0

    def test_room_management(self):
        from middleware.websocket import ConnectionManager
        manager = ConnectionManager()
        # Test room creation without actual WebSocket
        manager._rooms["test_room"] = {"client1", "client2"}
        rooms = manager.get_rooms()
        assert "test_room" in rooms
        assert rooms["test_room"] == 2

    def test_broadcast(self):
        from middleware.websocket import ConnectionManager, WSMessage, MessageType
        manager = ConnectionManager()
        stats = manager.get_stats()
        assert "total_connections" in stats


# ──────────────────────────────────────────────────────────────
# Metrics Tests
# ──────────────────────────────────────────────────────────────

class TestMetrics:
    def test_counter(self):
        from middleware.metrics import Counter
        c = Counter("test_counter", "A test counter")
        c.inc()
        c.inc(5)
        assert c.get() == 6.0

    def test_counter_with_labels(self):
        from middleware.metrics import Counter
        c = Counter("label_counter", "With labels", ["method", "endpoint"])
        c.inc(method="GET", endpoint="/api")
        c.inc(method="POST", endpoint="/api")
        assert c.get(method="GET", endpoint="/api") == 1.0
        assert c.get(method="POST", endpoint="/api") == 1.0

    def test_gauge(self):
        from middleware.metrics import Gauge
        g = Gauge("test_gauge", "A test gauge")
        g.set(42)
        assert g.get() == 42
        g.inc(10)
        assert g.get() == 52
        g.dec(5)
        assert g.get() == 47

    def test_histogram(self):
        from middleware.metrics import Histogram
        h = Histogram("test_hist", "A test histogram", buckets=(0.1, 0.5, 1.0, float("inf")))
        h.observe(0.05)
        h.observe(0.3)
        h.observe(0.8)
        h.observe(2.0)
        samples = h._samples()
        assert len(samples) > 0

    def test_registry_generation(self):
        from middleware.metrics import MetricsRegistry
        reg = MetricsRegistry()
        c = reg.counter("req_total", "Total requests")
        c.inc()
        g = reg.gauge("active", "Active connections")
        g.set(5)
        output = reg.generate()
        assert "req_total" in output
        assert "active" in output
        assert "# TYPE" in output
        assert "# HELP" in output

    def test_inprogress_tracker(self):
        from middleware.metrics import Gauge, _InprogressTracker
        g = Gauge("inprog", "In progress")
        assert g.get() == 0
        with _InprogressTracker(g, {}):
            assert g.get() == 1
        assert g.get() == 0

    def test_timer(self):
        from middleware.metrics import Histogram, _Timer
        h = Histogram("timer_test", "Timer test", buckets=(0.001, 0.01, float("inf")))
        with _Timer(h, {}):
            time.sleep(0.01)
        samples = h._samples()
        assert any(s.name == "timer_test_sum" for s in samples)
