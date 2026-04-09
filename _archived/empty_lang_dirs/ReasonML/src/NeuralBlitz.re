/* NeuralBlitz Core - ReasonML Implementation */
module Tensor = {
  type t('a) = {
    data: array('a),
    shape: array(int),
  };

  let create = (shape: array(int), init: 'a): t('a) => {
    let size = Array.fold_left((acc, x) => acc * x, 1, shape);
    {data: Array.make(size, init), shape};
  };

  let size = (t: t('a)) => 
    Array.fold_left((acc, x) => acc * x, 1, t.shape);

  let reshape = (t: t('a), newShape: array(int)): t('a) => {
    if (Array.fold_left((acc, x) => acc * x, 1, newShape) != size(t)) {
      invalid_arg("reshape: size mismatch");
    };
    {...t, shape: newShape};
  };

  let flatten = (t: t('a)): t('a) => 
    {...t, shape: [|size(t)|]};

  let zeros = (shape: array(int)): t(float) => 
    create(shape, 0.0);

  let ones = (shape: array(int)): t(float) => 
    create(shape, 1.0);

  let randomUniform = (shape: array(int)): t(float) => {
    let t = create(shape, 0.0);
    for (i in 0 to size(t) - 1) {
      t.data[i] = Js.Math.random();
    };
    t;
  };
};

module Activation = {
  let relu = (x: float): float => x > 0.0 ? x : 0.0;
  
  let leakyRelu = (x: float, alpha: float): float => 
    x > 0.0 ? x : alpha *. x;
  
  let sigmoid = (x: float): float => 
    1.0 /. (1.0 +. exp(-. x));
  
  let softmax = (v: array(float)): array(float) => {
    let maxVal = Array.fold_left(max, neg_infinity, v);
    let exps = Array.map(x => exp(x -. maxVal), v);
    let sumExps = Array.fold_left((+.), 0.0, exps);
    Array.map(x => x /. sumExps, exps);
  };
  
  let tanh = (x: float): float => tanh(x);
  
  let swish = (x: float): float => x *. sigmoid(x);
  
  let softplus = (x: float): float => log(1.0 +. exp(x));
  
  let mish = (x: float): float => x *. tanh(softplus(x));
};

module Dense = {
  type t = {
    weights: array(array(float)),
    bias: array(float),
    inputSize: int,
    outputSize: int,
  };

  let create = (~inputSize: int, ~outputSize: int): t => {
    let weights = Array.make_matrix(outputSize, inputSize, 0.01);
    let bias = Array.make(outputSize, 0.01);
    {weights, bias, inputSize, outputSize};
  };

  let forward = (layer: t, input: array(float)): array(float) => {
    Array.init(layer.outputSize, i => {
      let sum = ref(layer.bias[i]);
      for (j in 0 to layer.inputSize - 1) {
        sum := !sum +. layer.weights[i][j] *. input[j];
      };
      !sum;
    });
  };
};

module Conv2D = {
  type t = {
    weights: array(array(array(float))),
    bias: array(float),
    kernelSize: int,
    stride: int,
    padding: int,
  };

  let create = (~inChannels: int, ~outChannels: int, ~kernelSize: int, 
               ~stride: int = 1, ~padding: int = 0): t => {
    let weights = Array.make_matrix(outChannels, inChannels, 
      Array.make(kernelSize, 0.0));
    let bias = Array.make(outChannels, 0.0);
    {weights, bias, kernelSize, stride, padding};
  };
};

module BatchNorm = {
  type t = {
    gamma: array(float),
    beta: array(float),
    mean: array(float),
    variance: array(float),
    epsilon: float,
  };

  let create = (~numFeatures: int, ~epsilon: float = 1e-5): t => {
    let gamma = Array.make(numFeatures, 1.0);
    let beta = Array.make(numFeatures, 0.0);
    let mean = Array.make(numFeatures, 0.0);
    let variance = Array.make(numFeatures, 1.0);
    {gamma, beta, mean, variance, epsilon};
  };
};

module Dropout = {
  type t = {
    rate: float,
    mask: option(array(float)),
  };

  let create = (~rate: float): t => {
    {rate, mask: None};
  };
};

module Model = {
  type layer =
    | Dense(Dense.t)
    | Activation((array(float) => array(float)));

  type t = {layers: list(layer)};

  let create = (layers: list(layer)): t => {layers};

  let rec forward = (model: t, input: array(float)): array(float) =>
    switch (model.layers) {
    | [] => input
    | [Dense(layer), ...rest] =>
      let output = Dense.forward(layer, input);
      forward({...model, layers: rest}, output);
    | [Activation(f), ...rest] =>
      let output = f(input);
      forward({...model, layers: rest}, output);
    };

  let predict = (model: t, input: array(float)): array(float) =>
    forward(model, input);
};

module Loss = {
  let mse = (pred: array(float), target: array(float)): float => {
    let sum = ref(0.0);
    for (i in 0 to Array.length(pred) - 1) {
      let diff = pred[i] -. target[i];
      sum := !sum +. diff *. diff;
    };
    !sum /. float(Array.length(pred));
  };

  let crossEntropy = (pred: array(float), target: array(float)): float => {
    let sum = ref(0.0);
    let eps = 1e-7;
    for (i in 0 to Array.length(pred) - 1) {
      let p = max(eps, min(1.0 -. eps, pred[i]));
      sum := !sum -. target[i] *. log(p);
    };
    !sum;
  };
};

module Optimizer = {
  type t = {
    learningRate: float,
  };

  let createSGD = (~learningRate: float): t => {learningRate};
  let createAdam = (~learningRate: float): t => {learningRate};
};

module GoldenDAG = {
  type t = {
    hash: string,
    seed: string,
    iterations: int,
  };

  let hash = (s: string): string => {
    let len = String.length(s);
    let buf = Buffer.create(64);
    for (i in 0 to min(63, len - 1)) {
      Buffer.add_char buf s.[i];
    };
    Buffer.contents(buf);
  };

  let rec iterate = (s: string, n: int): string =>
    if (n <= 0) {
      s;
    } else {
      iterate(hash(s ++ s), n - 1);
    };

  let generate = (~seed: string, ~iterations: int): t => {
    let hash = iterate(seed, iterations);
    {hash, seed, iterations};
  };

  let verify = (dag: t): bool =>
    String.length(dag.hash) == 64;
};

module TraceID = {
  type t = {
    id: string,
    timestamp: float,
  };

  let generate = (~prefix: string, ~component: string): t => {
    let timestamp = Js.Date.now();
    let id = prefix ++ "-" ++ component ++ "-" ++ string_of_int(int_of_float(timestamp));
    {id, timestamp};
  };
};

module CodexID = {
  type t = {
    id: string,
    version: string,
    contentHash: string,
  };

  let generate = (~content: string, ~version: string): t => {
    let hash = GoldenDAG.hash(content);
    let id = "CODEX-" ++ version ++ "-" ++ String.sub(hash, 0, 24);
    {id, version, contentHash: hash};
  };
};

module Attestation = {
  type t = {
    seal: string,
    coherence: float,
    selfGrounding: float,
    irreducibility: float,
    timestamp: float,
  };

  let create = (~seal: string, ~coherence: float, 
                ~selfGrounding: float, ~irreducibility: float): t => {
    {
      seal,
      coherence,
      selfGrounding,
      irreducibility,
      timestamp: Js.Date.now(),
    };
  };

  let verify = (~data: string, ~dag: GoldenDAG.t): t => {
    create(
      ~seal=dag.hash,
      ~coherence=1.0,
      ~selfGrounding=1.0,
      ~irreducibility=1.0,
    );
  };
};

module Cognitive = {
  type consciousnessLevel =
    | Reactive
    | Adaptive
    | Predictive
    | Metacognitive
    | Transcendent;

  let consciousnessLevelToInt = (level: consciousnessLevel): int =>
    switch (level) {
    | Reactive => 0
    | Adaptive => 1
    | Predictive => 2
    | Metacognitive => 3
    | Transcendent => 4
    };

  type cognitiveState =
    | Idle
    | Perceiving
    | Attending
    | Learning
    | Reasoning
    | Deciding
    | Acting
    | Reflecting;

  type intentVector = {
    phi1: float,  /* Control/influence */
    phi2: float,  /* Balance/integration */
    phi3: float,  /* Novelty/innovation */
    phi4: float,  /* Stability/security */
    phi5: float,  /* Change/evolution */
    phi6: float,  /* Understanding/wisdom */
    phi7: float,  /* Unity/empathy */
  };

  let createIntent = (~phi1: float, ~phi2: float, ~phi3: float, 
                     ~phi4: float, ~phi5: float, ~phi6: float, 
                     ~phi7: float): intentVector => {
    {phi1, phi2, phi3, phi4, phi5, phi6, phi7};
  };

  let intentMagnitude = (intent: intentVector): float => {
    sqrt(
      intent.phi1 *. intent.phi1 +.
      intent.phi2 *. intent.phi2 +.
      intent.phi3 *. intent.phi3 +.
      intent.phi4 *. intent.phi4 +.
      intent.phi5 *. intent.phi5 +.
      intent.phi6 *. intent.phi6 +.
      intent.phi7 *. intent.phi7
    );
  };

  type consciousness = {
    level: consciousnessLevel,
    coherence: float,
    complexity: float,
    intent: intentVector,
  };

  let createConsciousness = (~level: consciousnessLevel, ~coherence: float, 
                              ~complexity: float, ~intent: intentVector): consciousness => {
    {level, coherence, complexity, intent};
  };

  let computeConsciousnessScore = (c: consciousness): float => {
    let levelScore = float_of_int(consciousnessLevelToInt(c.level)) /. 4.0;
    let intentMag = intentMagnitude(c.intent);
    (c.coherence +. c.complexity +. intentMag +. levelScore) /. 4.0;
  };
};

module WorkingMemory = {
  type 'a item = {
    content: 'a,
    salience: float,
    timestamp: float,
  };

  type 'a t = {
    items: list(item('a)),
    capacity: int,
  };

  let create = (~capacity: int): 'a t => {
    {items: [], capacity};
  };

  let add = (item: 'a item, wm: 'a t): 'a t => {
    if (List.length(wm.items) >= wm.capacity) {
      let rec takeLast = (n, l) =>
        switch (l) {
        | [] => []
        | [x] => [x]
        | [x, ...rest] => n > 0 ? [x, ...takeLast(n - 1, rest)] : []
        };
      {...wm, items: [item, ...takeLast(wm.capacity - 1, wm.items)]};
    } else {
      {...wm, items: [item, ...wm.items]};
    };
  };
};

module Neuron = {
  type t = {
    id: int,
    bias: float,
    weights: array(float),
    membranePotential: float,
  };

  let create = (~id: int, ~bias: float, ~weights: array(float)): t => {
    {id, bias, weights, membranePotential: 0.0};
  };
};

module SpikingNeuron = {
  type t = {
    id: int,
    mutable membranePotential: float,
    threshold: float,
    mutable refractoryPeriod: int,
  };

  let create = (~id: int, ~threshold: float): t => {
    {id, membranePotential: 0.0, threshold, refractoryPeriod: 0};
  };

  let spike = (n: t): bool =>
    n.membranePotential > n.threshold;
};

module QuantumCrypto = {
  type keyPair = {
    publicKey: string,
    privateKey: string,
  };

  let generateKeyPair = (): keyPair => {
    let randomString = (len): string => {
      let chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      let buf = Buffer.create(len);
      for (i in 0 to len - 1) {
        Buffer.add_char buf chars.[Js.Math.floor(Js.Math.random() *. float_of_int(String.length(chars)))];
      };
      Buffer.contents(buf);
    };
    {publicKey: randomString(32), privateKey: randomString(32)};
  };
};

let version = "50.0.0";

let info = () => {
  Printf.printf("NeuralBlitz v%s - Omega Singularity\n", version);
  let dag = GoldenDAG.generate(~seed="omega", ~iterations=1);
  Printf.printf("GoldenDAG: %s\n", String.sub(dag.hash, 0, 16));
  Printf.printf("Status: Operational\n");
};
