import re
import webbrowser

class SmartURLHandler:
    def __init__(self):
        self.website_mappings = {
            # Data Science & Tech
            'kaggle': 'https://www.kaggle.com',
            'github': 'https://www.github.com',
            'stackoverflow': 'https://stackoverflow.com',
            'google': 'https://www.google.com',
            'colab': 'https://colab.research.google.com',
            
            # E-commerce
            'amazon': 'https://www.amazon.com',
            'daraz': 'https://www.daraz.pk',
            'alibaba': 'https://www.alibaba.com',
            'flipkart': 'https://www.flipkart.com',
            'ebay': 'https://www.ebay.com',
            
            # Social & Media
            'youtube': 'https://www.youtube.com',
            'instagram': 'https://www.instagram.com',
            'twitter': 'https://www.twitter.com',
            'linkedin': 'https://www.linkedin.com',
            
            # News & Information
            'wikipedia': 'https://www.wikipedia.org',
            'bbc': 'https://www.bbc.com',
            'cnn': 'https://www.cnn.com',
            
            # Educational
            'coursera': 'https://www.coursera.org',
            'udemy': 'https://www.udemy.com',
            
            # Pakistani
            'urdupoint': 'https://www.urdupoint.com',
            'jang': 'https://jang.com.pk',
            'dawn': 'https://www.dawn.com'
        }
    
    def extract_url_from_query(self, query):
        """Extract URL from voice query - smart detection"""
        query = query.lower().strip()
        
        # Method 1: Direct URL match
        url_match = re.search(r'https?://[^\s]+', query)
        if url_match:
            url = url_match.group(0)
            return url, 'direct_url'
        
        # Method 2: Website name mapping
        for site_name, site_url in self.website_mappings.items():
            if site_name in query:
                return site_url, 'website_mapping'
        
        # Method 3: Common patterns
        if '.com' in query or '.org' in query or '.net' in query:
            domain_match = re.search(r'([a-zA-Z0-9-]+\.(com|org|net|edu|gov|pk))', query)
            if domain_match:
                domain = domain_match.group(1)
                return f"https://www.{domain}", 'domain_detection'
        
        return None, 'not_found'
    
    def smart_url_detection(self, query):
        """Smart URL detection"""
        url, detection_type = self.extract_url_from_query(query)
        
        if url:
            return {
                'success': True,
                'url': url,
                'detection_type': detection_type,
                'message': f"URL detected via {detection_type.replace('_', ' ')}"
            }
        else:
            words = query.split()
            for word in words:
                if word in self.website_mappings:
                    return {
                        'success': True,
                        'url': self.website_mappings[word],
                        'detection_type': 'keyword_mapping',
                        'message': f"Opening {word}"
                    }
            
            return {
                'success': False,
                'url': None,
                'detection_type': 'not_found',
                'message': "No valid URL or website name detected"
            }
    
    def is_shopping_website(self, url):
        """Check if URL is a shopping website"""
        shopping_keywords = ['amazon', 'daraz', 'alibaba', 'flipkart', 'ebay']
        return any(keyword in url.lower() for keyword in shopping_keywords)
    
    def open_website(self, query):
        """Open website based on query"""
        result = self.smart_url_detection(query)
        
        if result['success']:
            try:
                webbrowser.open(result['url'])
                return {
                    'success': True,
                    'url': result['url'],
                    'is_shopping': self.is_shopping_website(result['url']),
                    'message': f"Opening {result['url']}"
                }
            except Exception as e:
                return {
                    'success': False,
                    'url': result['url'],
                    'message': f"Error opening website: {e}"
                }
        else:
            return result