import re
import os
from datetime import datetime
import google.generativeai as genai

class NLPProcessor:
    def __init__(self):
        """Initialize NLP Processor with enhanced understanding capabilities"""
        self.conversation_history = []
        self.pending_tasks = []
        self.user_context = {}
        
        # Initialize Gemini AI
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.ai_enabled = True
            else:
                self.ai_enabled = False
                print("[Warning] Gemini API key not found. AI features disabled.")
        except Exception as e:
            self.ai_enabled = False
            print(f"[Warning] Could not initialize Gemini: {e}")
        
        # Command patterns for better understanding
        self.command_patterns = {
            'open': [
                r'\b(open|launch|start|run)\s+(.+)',
                r'\bcan you (open|launch|start)\s+(.+)',
                r'\bplease (open|launch|start)\s+(.+)'
            ],
            'close': [
                r'\b(close|exit|quit|stop)\s+(.+)',
                r'\bcan you (close|exit|quit)\s+(.+)',
                r'\bplease (close|exit|quit)\s+(.+)'
            ],
            'search': [
                r'\b(search|find|look for|google)\s+(.+)',
                r'\bcan you (search|find|look for)\s+(.+)',
                r'\bwhat is (.+)',
                r'\bwho is (.+)',
                r'\btell me about (.+)'
            ],
            'time': [
                r'\b(what|tell me|what\'s) (the |is the )?time',
                r'\bwhat time is it',
                r'\bcurrent time'
            ],
            'date': [
                r'\b(what|tell me|what\'s) (the |is the )?(date|day)',
                r'\bwhat\'s today',
                r'\btoday\'s date'
            ],
            'weather': [
                r'\b(weather|temperature|forecast)',
                r'\bhow\'s the weather',
                r'\bwhat\'s the weather like'
            ],
            'file': [
                r'\b(create|make|write)\s+(a |an )?file',
                r'\b(delete|remove|trash)\s+(.+)',
                r'\b(find|locate|search for)\s+file'
            ],
            'music': [
                r'\b(play|start|put on)\s+(music|song)',
                r'\b(pause|stop)\s+(music|song)',
                r'\bnext (song|track)',
                r'\bprevious (song|track)'
            ],
            'system': [
                r'\b(shutdown|restart|sleep|lock)\s+(computer|pc|system)',
                r'\bvolume (up|down|mute)',
                r'\bbrightness (up|down|increase|decrease)'
            ]
        }
        
        # Positive and negative words for sentiment analysis
        self.positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'happy', 'pleased', 'satisfied', 'love', 'like', 'best', 'perfect',
            'awesome', 'brilliant', 'superb', 'outstanding', 'nice', 'beautiful'
        ]
        
        self.negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'dislike', 'disappointed', 'angry', 'sad', 'frustrated', 'annoyed',
            'upset', 'unhappy', 'useless', 'boring', 'dull', 'slow'
        ]
        
    def process_command(self, query):
        """
        Main processing function that handles all NLP features
        Returns: dict with command type, action, parameters, sentiment
        """
        if not query:
            return None
        
        # Store in conversation history
        self.conversation_history.append({
            'query': query,
            'timestamp': datetime.now()
        })
        
        # Perform sentiment analysis
        sentiment = self.analyze_sentiment(query)
        
        # Understand command with better context
        command_info = self.understand_command(query)
        
        # Check for ambiguity
        if command_info['ambiguous']:
            clarification = self.resolve_ambiguity(query, command_info)
            command_info['clarification_needed'] = clarification
        
        # Check for multi-step tasks
        if self.is_multistep_task(query):
            steps = self.break_into_steps(query)
            command_info['multi_step'] = True
            command_info['steps'] = steps
        
        # Add sentiment to command info
        command_info['sentiment'] = sentiment
        
        # Use AI for complex understanding if enabled
        if self.ai_enabled and command_info['confidence'] < 0.7:
            ai_understanding = self.ai_understand(query)
            if ai_understanding:
                command_info['ai_suggestion'] = ai_understanding
        
        return command_info
    
    def understand_command(self, query):
        """Enhanced command understanding with pattern matching"""
        query = query.lower().strip()
        
        result = {
            'type': 'unknown',
            'action': None,
            'parameters': [],
            'original_query': query,
            'confidence': 0.0,
            'ambiguous': False
        }
        
        # Check each command pattern
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    result['type'] = cmd_type
                    result['confidence'] = 0.9
                    
                    # Extract parameters based on groups
                    if len(match.groups()) > 0:
                        result['action'] = match.group(1)
                        if len(match.groups()) > 1:
                            result['parameters'] = [g for g in match.groups()[1:] if g]
                    
                    return result
        
        # If no pattern matched, try keyword matching
        keywords = {
            'open': ['open', 'launch', 'start', 'run'],
            'close': ['close', 'exit', 'quit', 'shutdown'],
            'search': ['search', 'find', 'google', 'look'],
            'time': ['time', 'clock'],
            'date': ['date', 'day', 'today'],
            'weather': ['weather', 'temperature', 'forecast'],
            'file': ['file', 'document', 'folder'],
            'music': ['music', 'song', 'play', 'audio'],
            'system': ['volume', 'brightness', 'restart', 'shutdown']
        }
        
        for cmd_type, words in keywords.items():
            if any(word in query for word in words):
                result['type'] = cmd_type
                result['confidence'] = 0.5
                result['ambiguous'] = True
                break
        
        return result
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of user input"""
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        # Calculate sentiment score
        if positive_count > negative_count:
            sentiment_score = positive_count / len(words) if words else 0
            return {
                'type': 'positive',
                'score': min(sentiment_score * 10, 1.0),
                'confidence': 0.7 + (positive_count * 0.1)
            }
        elif negative_count > positive_count:
            sentiment_score = negative_count / len(words) if words else 0
            return {
                'type': 'negative',
                'score': min(sentiment_score * 10, 1.0),
                'confidence': 0.7 + (negative_count * 0.1)
            }
        else:
            return {
                'type': 'neutral',
                'score': 0.5,
                'confidence': 0.6
            }
    
    def is_multistep_task(self, query):
        """Check if query contains multiple tasks"""
        multi_step_indicators = [
            'and then', 'after that', 'then', 'next', 'finally',
            'first', 'second', 'also', 'additionally', 'and also'
        ]
        
        # Check for conjunctions indicating multiple tasks
        if any(indicator in query.lower() for indicator in multi_step_indicators):
            return True
        
        # Check for multiple command verbs
        command_verbs = ['open', 'close', 'search', 'play', 'stop', 'create', 'delete']
        verb_count = sum(1 for verb in command_verbs if verb in query.lower())
        
        return verb_count > 1
    
    def break_into_steps(self, query):
        """Break multi-step query into individual steps"""
        # Split by common separators
        separators = [
            'and then', 'after that', 'then', 'next', 'finally',
            'first', 'second', 'third', 'also', ', and'
        ]
        
        steps = [query]
        for separator in separators:
            if separator in query.lower():
                parts = re.split(separator, query, flags=re.IGNORECASE)
                steps = [part.strip() for part in parts if part.strip()]
                break
        
        # Process each step
        processed_steps = []
        for i, step in enumerate(steps):
            step_info = self.understand_command(step)
            step_info['step_number'] = i + 1
            processed_steps.append(step_info)
        
        return processed_steps
    
    def resolve_ambiguity(self, query, command_info):
        """Provide clarification for ambiguous commands"""
        clarifications = {
            'open': "Which application would you like me to open?",
            'close': "Which application should I close?",
            'search': "What would you like me to search for?",
            'file': "What file operation would you like to perform?",
            'music': "Would you like to play, pause, or control music?",
            'system': "What system operation would you like to perform?"
        }
        
        if command_info['confidence'] < 0.7:
            return clarifications.get(command_info['type'], 
                                     "Could you please be more specific about what you'd like me to do?")
        
        return None
    
    def ai_understand(self, query):
        """Use Gemini AI for complex command understanding"""
        if not self.ai_enabled:
            return None
        
        try:
            prompt = f"""
            Analyze this voice command and extract the intent:
            Command: "{query}"
            
            Provide:
            1. Main intent/action
            2. Target/object
            3. Any parameters
            4. Confidence level (0-1)
            
            Format as: ACTION | TARGET | PARAMETERS | CONFIDENCE
            Example: open | chrome browser | none | 0.95
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                parts = response.text.strip().split('|')
                if len(parts) >= 4:
                    return {
                        'action': parts[0].strip(),
                        'target': parts[1].strip(),
                        'parameters': parts[2].strip(),
                        'ai_confidence': float(parts[3].strip())
                    }
        except Exception as e:
            print(f"[AI Understanding Error]: {e}")
        
        return None
    
    def get_conversation_context(self):
        """Return recent conversation history for context"""
        return self.conversation_history[-5:] if self.conversation_history else []
    
    def add_task_to_queue(self, task):
        """Add multi-step task to pending queue"""
        self.pending_tasks.append(task)
    
    def get_next_task(self):
        """Get next task from queue"""
        if self.pending_tasks:
            return self.pending_tasks.pop(0)
        return None
    
    def update_user_context(self, key, value):
        """Store user preferences and context"""
        self.user_context[key] = value
    
    def get_user_context(self, key):
        """Retrieve user context"""
        return self.user_context.get(key, None)
