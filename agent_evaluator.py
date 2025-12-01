# agent_evaluator.py
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import threading

class AgentEvaluator:
    """
    Evaluates agent performance with metrics and scoring
    """
    
    def __init__(self):
        self.evaluation_log = "agent_evaluation.json"
        self.metrics = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'response_times': [],
            'command_types': {},
            'error_types': {},
            'user_satisfaction': []
        }
        self.start_time = time.time()
        
    def log_command(self, command: str, success: bool, response_time: float, 
                   error: str = None):
        """Log a command execution"""
        self.metrics['total_commands'] += 1
        
        if success:
            self.metrics['successful_commands'] += 1
        else:
            self.metrics['failed_commands'] += 1
            if error:
                self.metrics['error_types'][error] = self.metrics['error_types'].get(error, 0) + 1
        
        self.metrics['response_times'].append(response_time)
        
        # Track command types
        cmd_type = self._categorize_command(command)
        self.metrics['command_types'][cmd_type] = self.metrics['command_types'].get(cmd_type, 0) + 1
        
        # Save to file periodically
        if self.metrics['total_commands'] % 10 == 0:
            self.save_evaluation()
    
    def add_feedback(self, feedback: str, score: int):
        """Add user feedback (1-10 score)"""
        self.metrics['user_satisfaction'].append({
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback,
            'score': score
        })
    
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        avg_response_time = sum(self.metrics['response_times']) / len(self.metrics['response_times']) if self.metrics['response_times'] else 0
        
        uptime = time.time() - self.start_time
        
        return {
            'uptime_hours': uptime / 3600,
            'success_rate': (self.metrics['successful_commands'] / self.metrics['total_commands']) * 100 if self.metrics['total_commands'] > 0 else 0,
            'average_response_time': avg_response_time,
            'total_commands': self.metrics['total_commands'],
            'command_breakdown': self.metrics['command_types'],
            'common_errors': dict(sorted(self.metrics['error_types'].items(), key=lambda x: x[1], reverse=True)[:5]),
            'user_satisfaction_average': sum([f['score'] for f in self.metrics['user_satisfaction']]) / len(self.metrics['user_satisfaction']) if self.metrics['user_satisfaction'] else 0
        }
    
    def evaluate_agent_conversation(self, conversation: List[Dict]) -> Dict:
        """Evaluate conversation quality"""
        if not conversation:
            return {'score': 0, 'feedback': 'No conversation'}
        
        scores = {
            'relevance': self._score_relevance(conversation),
            'helpfulness': self._score_helpfulness(conversation),
            'efficiency': self._score_efficiency(conversation),
            'naturalness': self._score_naturalness(conversation)
        }
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            'overall_score': overall_score,
            'category_scores': scores,
            'conversation_length': len(conversation),
            'recommendations': self._generate_recommendations(scores)
        }
    
    def _categorize_command(self, command: str) -> str:
        """Categorize command type"""
        command = command.lower()
        categories = {
            'information': ['what', 'who', 'when', 'where', 'why', 'how', 'tell me', 'explain'],
            'action': ['open', 'close', 'send', 'create', 'delete', 'play', 'stop', 'search'],
            'system': ['volume', 'brightness', 'shutdown', 'restart', 'sleep'],
            'communication': ['email', 'message', 'call', 'remind'],
            'entertainment': ['music', 'video', 'joke', 'story']
        }
        
        for category, keywords in categories.items():
            if any(keyword in command for keyword in keywords):
                return category
        
        return 'other'
    
    def _score_relevance(self, conversation: List[Dict]) -> float:
        """Score relevance of responses"""
        # Simple implementation - could be enhanced with NLP
        return 0.8
    
    def _score_helpfulness(self, conversation: List[Dict]) -> float:
        """Score helpfulness of responses"""
        helpful_keywords = ['here is', 'i found', 'successfully', 'done', 'completed']
        score = 0
        for turn in conversation:
            if any(keyword in turn.get('response', '').lower() for keyword in helpful_keywords):
                score += 0.1
        return min(score, 1.0)
    
    def _score_efficiency(self, conversation: List[Dict]) -> float:
        """Score efficiency (fewer turns for task completion)"""
        # Lower is better for efficiency
        if len(conversation) <= 3:
            return 1.0
        elif len(conversation) <= 5:
            return 0.8
        elif len(conversation) <= 8:
            return 0.6
        else:
            return 0.4
    
    def _score_naturalness(self, conversation: List[Dict]) -> float:
        """Score natural language flow"""
        # Simple proxy - check for greetings and polite phrases
        natural_phrases = ['hello', 'hi', 'please', 'thank you', 'you\'re welcome', 'how can i help']
        score = 0
        for turn in conversation:
            if any(phrase in turn.get('response', '').lower() for phrase in natural_phrases):
                score += 0.2
        return min(score, 1.0)
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        if scores['relevance'] < 0.7:
            recommendations.append("Improve response relevance to user queries")
        if scores['helpfulness'] < 0.7:
            recommendations.append("Provide more detailed and helpful responses")
        if scores['efficiency'] < 0.7:
            recommendations.append("Reduce number of turns needed to complete tasks")
        if scores['naturalness'] < 0.7:
            recommendations.append("Use more natural language and polite phrases")
        
        return recommendations if recommendations else ["Good performance overall!"]
    
    def save_evaluation(self):
        """Save evaluation data to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'performance_report': self.get_performance_report()
        }
        
        try:
            with open(self.evaluation_log, 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"Error saving evaluation: {e}")