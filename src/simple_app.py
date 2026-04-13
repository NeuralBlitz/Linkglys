#!/usr/bin/env python3
"""OpenCode LRS Code Analysis Hub — Honest benchmarks, real pattern analysis."""

import os
import re
import time

from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenCode LRS Code Analysis Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="max-w-6xl mx-auto p-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-4">🧠 OpenCode LRS Code Analysis Hub</h1>
            <p class="text-xl text-gray-600 mb-6">Fast pattern-based code analysis</p>
            <div class="flex justify-center space-x-4 mb-8">
                <div class="bg-purple-100 text-purple-800 px-4 py-2 rounded-full text-sm font-medium">Pattern Detection</div>
                <div class="bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium">Instant Results</div>
                <div class="bg-green-100 text-green-800 px-4 py-2 rounded-full text-sm font-medium">Real Timing</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">📝 Code Input</h2>
                <p class="text-gray-600 mb-4">Paste Python, JavaScript, or Java code for pattern analysis.</p>

                <textarea id="codeInput" rows="15" class="w-full p-4 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent" placeholder="# Enter your code here...
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"></textarea>

                <div class="mt-6 flex space-x-4">
                    <button onclick="analyzeCode()" class="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition duration-200 flex items-center">
                        <span class="mr-2">🔍</span> Analyze Code
                    </button>
                    <button onclick="clearCode()" class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-3 rounded-lg font-medium transition duration-200">Clear</button>
                    <button onclick="loadSample()" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium transition duration-200">Load Sample</button>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">🎯 Analysis Results</h2>

                <div class="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-2">
                            <div id="statusIndicator" class="w-3 h-3 bg-gray-400 rounded-full"></div>
                            <span id="statusText" class="text-sm font-medium text-gray-700">Ready for analysis</span>
                        </div>
                        <div class="text-right">
                            <div class="text-xs text-gray-500">Analysis Time</div>
                            <div id="analysisTime" class="text-sm font-medium text-green-600">-- ms</div>
                        </div>
                    </div>
                </div>

                <div class="mb-6 grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-3 rounded-lg text-center">
                        <div id="linesAnalyzed" class="text-lg font-bold text-blue-600">--</div>
                        <div class="text-xs text-blue-700">Lines Analyzed</div>
                    </div>
                    <div class="bg-green-50 p-3 rounded-lg text-center">
                        <div id="patternsFound" class="text-lg font-bold text-green-600">--</div>
                        <div class="text-xs text-green-700">Patterns Found</div>
                    </div>
                </div>

                <div id="resultsContainer">
                    <div class="text-center text-gray-500 py-12">
                        <div class="text-6xl mb-4">🔍</div>
                        <h3 class="text-lg font-medium mb-2">Ready for Analysis</h3>
                        <p class="text-sm">Enter code and click "Analyze Code" to see pattern detection results.</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">⚡ How It Works</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <h3 class="font-medium text-gray-900 mb-2">🔍 Pattern Detection</h3>
                    <ul class="text-sm text-gray-700 space-y-1">
                        <li>• Functions, classes, methods</li>
                        <li>• Loops (for, while, list comps)</li>
                        <li>• Conditionals (if/elif/else)</li>
                        <li>• Imports and decorators</li>
                    </ul>
                </div>
                <div>
                    <h3 class="font-medium text-gray-900 mb-2">📊 Complexity Metrics</h3>
                    <ul class="text-sm text-gray-700 space-y-1">
                        <li>• Cyclomatic complexity estimate</li>
                        <li>• Nesting depth analysis</li>
                        <li>• Code-to-comment ratio</li>
                        <li>• Average function length</li>
                    </ul>
                </div>
                <div>
                    <h3 class="font-medium text-gray-900 mb-2">💡 Recommendations</h3>
                    <ul class="text-sm text-gray-700 space-y-1">
                        <li>• Type hints suggestion</li>
                        <li>• Docstring coverage</li>
                        <li>• Complexity warnings</li>
                        <li>• Best practice tips</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        function analyzeCode() {
            const codeInput = document.getElementById('codeInput');
            const code = codeInput.value.trim();
            if (!code) { alert('Please enter some code'); return; }

            document.getElementById('statusIndicator').className = 'w-3 h-3 bg-yellow-500 rounded-full animate-pulse';
            document.getElementById('statusText').textContent = 'Analyzing...';

            fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code})
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('statusIndicator').className = 'w-3 h-3 bg-green-500 rounded-full';
                document.getElementById('statusText').textContent = 'Analysis Complete';
                document.getElementById('analysisTime').textContent = data.analysis_time + ' ms';
                document.getElementById('linesAnalyzed').textContent = data.lines_analyzed;
                document.getElementById('patternsFound').textContent = data.patterns_found;
                displayResults(data);
            })
            .catch(err => {
                document.getElementById('statusIndicator').className = 'w-3 h-3 bg-red-500 rounded-full';
                document.getElementById('statusText').textContent = 'Error: ' + err.message;
            });
        }

        function displayResults(data) {
            const i = data.insights;
            const c = document.getElementById('resultsContainer');
            c.innerHTML = `
                <div class="space-y-4">
                    <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
                        <h3 class="font-medium text-blue-900 mb-2">🔍 Patterns Detected</h3>
                        <div class="grid grid-cols-2 gap-4 text-sm text-blue-800">
                            <div><strong>Functions:</strong> ${i.functions}</div>
                            <div><strong>Classes:</strong> ${i.classes}</div>
                            <div><strong>Conditionals:</strong> ${i.conditionals}</div>
                            <div><strong>Loops:</strong> ${i.loops}</div>
                            <div><strong>Imports:</strong> ${i.imports}</div>
                            <div><strong>Comments:</strong> ${i.comments}</div>
                        </div>
                        <p class="mt-2 text-sm text-blue-700"><strong>Complexity:</strong> ${i.complexity}</p>
                    </div>
                    <div class="bg-purple-50 border-l-4 border-purple-400 p-4 rounded">
                        <h3 class="font-medium text-purple-900 mb-2">💡 Recommendations</h3>
                        <ul class="text-sm text-purple-800 space-y-1">
                            ${data.recommendations.map(r => `<li>• ${r}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="bg-gray-50 border-l-4 border-gray-400 p-4 rounded">
                        <h3 class="font-medium text-gray-900 mb-2">📊 Metrics</h3>
                        <div class="text-sm text-gray-800">
                            <p><strong>Analysis Time:</strong> ${data.analysis_time} ms (measured, not simulated)</p>
                            <p><strong>Comment Ratio:</strong> ${i.comment_ratio}%</p>
                            <p><strong>Max Nesting Depth:</strong> ${i.max_nesting}</p>
                        </div>
                    </div>
                </div>
            `;
        }

        function clearCode() {
            document.getElementById('codeInput').value = '';
            document.getElementById('resultsContainer').innerHTML = `
                <div class="text-center text-gray-500 py-12">
                    <div class="text-6xl mb-4">🔍</div>
                    <h3 class="text-lg font-medium mb-2">Ready for Analysis</h3>
                    <p class="text-sm">Enter code and click "Analyze Code".</p>
                </div>
            `;
            document.getElementById('statusIndicator').className = 'w-3 h-3 bg-gray-400 rounded-full';
            document.getElementById('statusText').textContent = 'Ready for analysis';
            document.getElementById('analysisTime').textContent = '-- ms';
            document.getElementById('linesAnalyzed').textContent = '--';
            document.getElementById('patternsFound').textContent = '--';
        }

        function loadSample() {
            document.getElementById('codeInput').value = `import asyncio
from typing import List, Optional
from dataclasses import dataclass

# A task with priority and completion tracking
@dataclass
class Task:
    id: int
    title: str
    completed: bool = False
    priority: str = "medium"

class TaskManager:
    # Manages a collection of tasks with filtering
    def __init__(self):
        self.tasks = {}
        self.next_id = 1

    def add_task(self, title: str, priority: str = "medium") -> Task:
        # Add a new task and return it
        task = Task(id=self.next_id, title=title, priority=priority)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def complete_task(self, task_id: int) -> bool:
        # Mark a task as completed
        task = self.tasks.get(task_id)
        if task:
            task.completed = True
            return True
        return False

    def get_pending(self) -> List[Task]:
        return [t for t in self.tasks.values() if not t.completed]

    def get_by_priority(self, priority: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.priority == priority]

if __name__ == "__main__":
    manager = TaskManager()
    manager.add_task("Review code", "high")
    manager.add_task("Write tests", "medium")
    pending = manager.get_pending()
    print(f"Pending: {len(pending)}")`;
        }

        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('statusText').textContent = 'Ready for analysis';
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'success': False, 'error': 'Invalid or missing JSON body'}), 400
    code = data.get('code', '')

    start_time = time.time()

    # ── Pattern Detection ──
    lines = code.split('\n')
    functions = len(re.findall(r'\bdef\s+\w+', code))
    classes = len(re.findall(r'\bclass\s+\w+', code))
    conditionals = len(re.findall(r'\b(if|elif|else)\b', code))
    loops = len(re.findall(r'\b(for|while)\b', code))
    imports = len(re.findall(r'\b(import|from)\s+\w+', code))
    comments = len(re.findall(r'#.*$', code, re.MULTILINE))
    decorators = len(re.findall(r'@\w+', code))
    try_blocks = len(re.findall(r'\btry\b', code))
    async_defs = len(re.findall(r'\basync\s+def\b', code))
    list_comps = len(re.findall(r'\[.*\bfor\b.*\bin\b.*\]', code))

    # ── Complexity Metrics ──
    # Cyclomatic complexity estimate: 1 + branches
    complexity = 1 + len(re.findall(r'\b(if|elif|for|while|and|or|except)\b', code))
    complexity_label = "Low" if complexity < 10 else "Medium" if complexity < 20 else "High"

    # Max nesting depth (indentation-based)
    max_nesting = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            depth = indent // 4
            max_nesting = max(max_nesting, depth)

    # Comment ratio
    total_lines = len([line for line in lines if line.strip()])
    comment_ratio = round((comments / total_lines * 100), 1) if total_lines > 0 else 0

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # ── Recommendations ──
    recommendations = []
    if functions > 0 and 'def ' in code and ': ' not in code:
        recommendations.append("Consider adding type hints to function signatures")
    if comments == 0 and total_lines > 5:
        recommendations.append("No comments found — consider adding docstrings")
    if max_nesting > 3:
        recommendations.append(f"Max nesting depth is {max_nesting} — consider extracting helper functions")
    if complexity > 15:
        recommendations.append(f"Complexity score {complexity} — consider breaking into smaller functions")
    if comment_ratio < 10 and total_lines > 10:
        recommendations.append(f"Comment ratio is {comment_ratio}% — aim for 15-20%")
    if 'class ' in code and 'def __init__' not in code:
        recommendations.append("Class found without __init__ — consider adding a constructor")
    if async_defs > 0:
        recommendations.append("Async functions detected — ensure proper await/asyncio.run usage")
    if list_comps > 3:
        recommendations.append("Multiple list comprehensions — ensure readability isn't compromised")
    if not recommendations:
        recommendations.append("Code looks clean — no major issues detected")

    patterns_total = functions + classes + conditionals + loops + imports + comments + decorators

    return jsonify({
        'success': True,
        'analysis_time': elapsed_ms,
        'lines_analyzed': len(lines),
        'patterns_found': patterns_total,
        'insights': {
            'functions': functions,
            'classes': classes,
            'conditionals': conditionals,
            'loops': loops,
            'imports': imports,
            'comments': comments,
            'decorators': decorators,
            'try_blocks': try_blocks,
            'async_functions': async_defs,
            'complexity': f"{complexity} ({complexity_label})",
            'max_nesting': max_nesting,
            'comment_ratio': comment_ratio,
        },
        'recommendations': recommendations,
    })

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=8080, debug=debug_mode)
