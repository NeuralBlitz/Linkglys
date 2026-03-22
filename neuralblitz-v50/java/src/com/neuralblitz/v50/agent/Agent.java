package com.neuralblitz.v50.agent;

import com.neuralblitz.v50.core.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;
import java.time.*;

public class Agent implements Comparable<Agent>, Serializable {
    private static final long serialVersionUID = 1L;
    
    private final long id;
    private final String uuid;
    private String name;
    private volatile AgentState state;
    private volatile double trustScore;
    private volatile double performanceScore;
    private final AtomicLong taskCount;
    private final AtomicLong successCount;
    private final long createdAt;
    private volatile long lastActive;
    
    private final List<Capability> capabilities;
    private final Map<Long, Double> relationships;
    private final Set<String> tags;
    private final transient ReadWriteLock lock;
    
    public Agent(long id, String name) {
        this(id, name, AgentState.IDLE);
    }
    
    public Agent(long id, String name, AgentState state) {
        this.id = id;
        this.uuid = UUID.generate();
        this.name = name;
        this.state = state;
        this.trustScore = 0.5;
        this.performanceScore = 0.0;
        this.taskCount = new AtomicLong(0);
        this.successCount = new AtomicLong(0);
        this.createdAt = System.currentTimeMillis();
        this.lastActive = createdAt;
        this.capabilities = new CopyOnWriteArrayList<>();
        this.relationships = new ConcurrentHashMap<>();
        this.tags = ConcurrentHashMap.newKeySet();
        this.lock = new ReentrantReadWriteLock();
    }
    
    public long getId() { return id; }
    public String getUuid() { return uuid; }
    public String getName() { return name; }
    public AgentState getState() { return state; }
    public double getTrustScore() { return trustScore; }
    public double getPerformanceScore() { return performanceScore; }
    public long getCreatedAt() { return createdAt; }
    public long getLastActive() { return lastActive; }
    
    public List<Capability> getCapabilities() { return new ArrayList<>(capabilities); }
    public Map<Long, Double> getRelationships() { return new HashMap<>(relationships); }
    public Set<String> getTags() { return new HashSet<>(tags); }
    
    public void setName(String name) { this.name = name; }
    public void setState(AgentState state) {
        lock.writeLock().lock();
        try {
            this.state = state;
            this.lastActive = System.currentTimeMillis();
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void addCapability(CapabilityKernel kernel, double proficiency) {
        capabilities.add(new Capability(kernel, proficiency));
    }
    
    public void addTag(String tag) {
        tags.add(tag);
    }
    
    public void updateTrustScore(double delta) {
        lock.writeLock().lock();
        try {
            trustScore = Math.max(AgentConstants.MIN_TRUST, 
                                 Math.min(AgentConstants.MAX_TRUST, trustScore + delta));
            lastActive = System.currentTimeMillis();
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void recordTaskCompletion(boolean success) {
        lock.writeLock().lock();
        try {
            taskCount.incrementAndGet();
            if (success) successCount.incrementAndGet();
            
            if (taskCount.get() > 0) {
                performanceScore = (double) successCount.get() / taskCount.get();
            }
            lastActive = System.currentTimeMillis();
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void updateRelationship(Long otherId, double trustDelta) {
        lock.writeLock().lock();
        try {
            double current = relationships.getOrDefault(otherId, 0.5);
            relationships.put(otherId, Math.max(AgentConstants.MIN_TRUST,
                Math.min(AgentConstants.MAX_TRUST, current + trustDelta)));
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public double getRelationship(Long otherId) {
        lock.readLock().lock();
        try {
            return relationships.getOrDefault(otherId, 0.0);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public boolean canHandleTask(Task task) {
        if (!isAvailable()) return false;
        
        List<CapabilityKernel> required = task.getRequiredCapabilities();
        if (required.isEmpty()) return true;
        
        for (CapabilityKernel req : required) {
            boolean hasCap = capabilities.stream()
                .anyMatch(c -> c.kernel == req && c.proficiency >= 0.5);
            if (!hasCap) return false;
        }
        return true;
    }
    
    public boolean isAvailable() {
        return state == AgentState.IDLE || state == AgentState.ACTIVE;
    }
    
    public Task executeTask(Task task) {
        setState(AgentState.ACTIVE);
        task.setState(TaskState.RUNNING);
        task.setExecutorId(id);
        
        Logger.getInstance().info("Agent " + name + " executing task " + task.getId());
        
        boolean success = performTaskExecution(task);
        
        if (success) {
            task.setState(TaskState.COMPLETED);
            recordTaskCompletion(true);
            updateTrustScore(0.01);
        } else {
            task.setState(TaskState.FAILED);
            recordTaskCompletion(false);
            updateTrustScore(-0.02);
        }
        
        setState(AgentState.IDLE);
        return task;
    }
    
    protected boolean performTaskExecution(Task task) {
        try {
            Thread.sleep(10);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return true;
    }
    
    @Override
    public int compareTo(Agent other) {
        return Double.compare(other.trustScore, this.trustScore);
    }
    
    public static class Capability {
        public final CapabilityKernel kernel;
        public final double proficiency;
        public final List<String> tags;
        
        public Capability(CapabilityKernel kernel, double proficiency) {
            this.kernel = kernel;
            this.proficiency = proficiency;
            this.tags = new ArrayList<>();
        }
    }
}

public class SpecializedAgent extends Agent {
    private final CapabilityKernel primaryKernel;
    
    public SpecializedAgent(long id, String name, CapabilityKernel primaryKernel) {
        super(id, name);
        this.primaryKernel = primaryKernel;
        addCapability(primaryKernel, 1.0);
    }
    
    public CapabilityKernel getPrimaryKernel() { return primaryKernel; }
    
    @Override
    public Task executeTask(Task task) {
        Logger.getInstance().debug("SpecializedAgent " + getName() + 
            " executing task with primary kernel " + primaryKernel);
        return super.executeTask(task);
    }
}

public class AgentCluster {
    private final long id;
    private final String name;
    private final List<Agent> members;
    private volatile long leaderId;
    private final ReadWriteLock lock;
    
    public AgentCluster(long id, String name) {
        this.id = id;
        this.name = name;
        this.members = new CopyOnWriteArrayList<>();
        this.leaderId = AgentConstants.INVALID_ID;
        this.lock = new ReentrantReadWriteLock();
    }
    
    public long getId() { return id; }
    public String getName() { return name; }
    public List<Agent> getMembers() { return new ArrayList<>(members); }
    public int getSize() { return members.size(); }
    
    public void addMember(Agent agent) {
        lock.writeLock().lock();
        try {
            if (!members.contains(agent)) {
                members.add(agent);
                if (leaderId == AgentConstants.INVALID_ID) {
                    leaderId = agent.getId();
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public void removeMember(long agentId) {
        lock.writeLock().lock();
        try {
            members.removeIf(a -> a.getId() == agentId);
            if (leaderId == agentId && !members.isEmpty()) {
                leaderId = members.get(0).getId();
            }
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public Agent getLeader() {
        lock.readLock().lock();
        try {
            return members.stream()
                .filter(a -> a.getId() == leaderId)
                .findFirst()
                .orElse(null);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public List<Agent> getAvailableAgents() {
        lock.readLock().lock();
        try {
            return members.stream()
                .filter(Agent::isAvailable)
                .collect(Collectors.toList());
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public double getAverageTrust() {
        lock.readLock().lock();
        try {
            if (members.isEmpty()) return 0.0;
            return members.stream()
                .mapToDouble(Agent::getTrustScore)
                .average()
                .orElse(0.0);
        } finally {
            lock.readLock().unlock();
        }
    }
}

public class AgentRegistry {
    private static final AgentRegistry INSTANCE = new AgentRegistry();
    
    private final Map<Long, Agent> agents;
    private final Map<String, Long> uuidMap;
    private final AtomicLong nextAgentId;
    private final ReadWriteLock lock;
    
    private AgentRegistry() {
        this.agents = new ConcurrentHashMap<>();
        this.uuidMap = new ConcurrentHashMap<>();
        this.nextAgentId = new AtomicLong(1);
        this.lock = new ReentrantReadWriteLock();
    }
    
    public static AgentRegistry getInstance() { return INSTANCE; }
    
    public Agent registerAgent(String name) {
        return registerAgent(name, AgentState.IDLE);
    }
    
    public Agent registerAgent(String name, AgentState state) {
        long id = nextAgentId.getAndIncrement();
        Agent agent = new Agent(id, name, state);
        
        lock.writeLock().lock();
        try {
            agents.put(id, agent);
            uuidMap.put(agent.getUuid(), id);
        } finally {
            lock.writeLock().unlock();
        }
        
        Logger.getInstance().info("Registered agent: " + name + " (ID: " + id + ")");
        return agent;
    }
    
    public void unregisterAgent(long id) {
        lock.writeLock().lock();
        try {
            Agent agent = agents.remove(id);
            if (agent != null) {
                uuidMap.remove(agent.getUuid());
            }
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public Agent getAgent(long id) {
        return agents.get(id);
    }
    
    public Agent getAgentByUuid(String uuid) {
        lock.readLock().lock();
        try {
            Long id = uuidMap.get(uuid);
            return id != null ? agents.get(id) : null;
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public List<Agent> getAllAgents() {
        return new ArrayList<>(agents.values());
    }
    
    public List<Agent> getAgentsByState(AgentState state) {
        return agents.values().stream()
            .filter(a -> a.getState() == state)
            .collect(Collectors.toList());
    }
    
    public List<Agent> getAgentsByCapability(CapabilityKernel kernel) {
        return agents.values().stream()
            .filter(a -> a.getCapabilities().stream()
                .anyMatch(c -> c.kernel == kernel))
            .collect(Collectors.toList());
    }
    
    public List<Agent> getAvailableAgents() {
        return agents.values().stream()
            .filter(Agent::isAvailable)
            .collect(Collectors.toList());
    }
    
    public int getAgentCount() {
        return agents.size();
    }
}

public class AgentFactory {
    public static Agent createReasoningAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.REASONING);
        agent.addCapability(CapabilityKernel.PLANNING, 0.8);
        agent.addCapability(CapabilityKernel.LEARNING, 0.7);
        return agent;
    }
    
    public static Agent createPerceptionAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.PERCEPTION);
        agent.addCapability(CapabilityKernel.MONITORING, 0.9);
        return agent;
    }
    
    public static Agent createActionAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.ACTION);
        agent.addCapability(CapabilityKernel.COMMUNICATION, 0.7);
        return agent;
    }
    
    public static Agent createGovernanceAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.GOVERNANCE);
        agent.addCapability(CapabilityKernel.VERIFICATION, 0.9);
        return agent;
    }
    
    public static Agent createVerificationAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.VERIFICATION);
        agent.addCapability(CapabilityKernel.GOVERNANCE, 0.8);
        return agent;
    }
    
    public static Agent createAdaptiveAgent(long id, String name) {
        Agent agent = new SpecializedAgent(id, name, CapabilityKernel.ADAPTATION);
        agent.addCapability(CapabilityKernel.LEARNING, 0.9);
        agent.addCapability(CapabilityKernel.REASONING, 0.7);
        return agent;
    }
}
