"""
Email analyzer module.
Uses LLM to determine if an email is necessary or not.
"""

from loguru import logger

class EmailAnalyzer:
    """Analyzes emails using LLM to determine if they are necessary."""
    
    def __init__(self, llm_client, body_preview_length=1000):
        """
        Initialize the email analyzer.
        
        Args:
            llm_client: LLM client (e.g., OpenRouterClient)
            body_preview_length (int): Length of email body to include in analysis
        """
        self.llm_client = llm_client
        self.body_preview_length = body_preview_length
        logger.debug(f"Initialized EmailAnalyzer with body preview length: {body_preview_length}")
    
    def check_necessity(self, email_data):
        """
        Use LLM to determine if an email is necessary.
        
        Args:
            email_data (dict): Email data including subject, sender, date, and body
            
        Returns:
            bool: True if necessary, False if unnecessary
        """
        # Prepare system prompt
        system_prompt = """
        You are an AI assistant that analyzes emails to determine if they are necessary to keep in the inbox.
        You should respond with ONLY "YES" or "NO" followed by a very brief explanation.
        """
        
        # Prepare user prompt for the LLM
        prompt = self._create_analysis_prompt(email_data)
        
        try:
            # Get response from LLM
            logger.debug(f"Analyzing email: {email_data['subject']}")
            response_text = self.llm_client.generate_response(prompt, system_prompt)
            
            # Parse the response
            return self._parse_necessity_response(response_text, email_data)
            
        except Exception as e:
            logger.error(f"Error analyzing email: {str(e)}")
            # In case of any error, default to keeping the email
            return True
    
    def _create_analysis_prompt(self, email_data):
        """
        Create a prompt for the LLM to analyze the email.
        
        Args:
            email_data (dict): Email data
            
        Returns:
            str: Analysis prompt
        """
        # Truncate body to specified length
        body = email_data.get('body', '')[:self.body_preview_length]
        
        prompt = f"""
        I need to determine if this email is necessary to keep in my inbox. Analyze it carefully.

        Subject: {email_data.get('subject', '(No Subject)')}
        From: {email_data.get('sender', '(No Sender)')}
        Date: {email_data.get('date', '(No Date)')}
        
        Email snippet: {email_data.get('snippet', '(No Snippet)')}
        
        Email content:
        {body}
        
        NECESSARY EMAILS (YOU MUST ANSWER "YES" FOR THESE):
        
        1. Order Confirmations and Shipping Updates:
           - Online purchase confirmations (Amazon, eBay, etc.)
           - Order shipment notifications with tracking numbers
           - Delivery confirmations
           - Return or refund confirmations
        
        2. Financial Information:
           - Bank statements and transaction alerts for actual transactions
           - Credit card statements and alerts for actual charges
           - Bill payment confirmations
           - Tax documents and receipts
           - Receipts for purchases or donations
        
        3. Personal Communications:
           - Emails from friends, family, or colleagues
           - Direct personal messages (not mass emails with personalization)
           - Responses to inquiries you've made
        
        4. Work and Professional:
           - Job-related emails from colleagues and clients
           - Project updates requiring review
           - Meeting invitations and calendar updates
           - Emails from your boss or team members
        
        5. Account and Security:
           - Password resets you requested
           - Security alerts for your accounts
           - Verification codes
           - Important account changes (not routine updates)
        
        6. Travel and Events:
           - Flight/hotel/car rental confirmations
           - Boarding passes
           - Event tickets
           - Reservation confirmations
           - Appointment reminders
        
        7. Educational:
           - Course communications from instructors
           - Assignment feedback
           - School announcements affecting you directly
        
        8. Required Actions:
           - Emails that explicitly request your response or action
           - Legal notices requiring attention
           - Time-sensitive information
        
        UNNECESSARY EMAILS (YOU MUST ANSWER "NO" FOR THESE):
        
        1. Marketing and Promotions:
           - Sales announcements
           - "Limited time offers"
           - Discount codes not related to recent purchases
           - Product recommendations
           - Newsletter digests
           - Daily/weekly deals
        
        2. Automated Updates:
           - Social media notifications
           - News digests or alerts
           - App usage summaries
           - "We miss you" emails
           - Platform updates not requiring action
        
        3. Bulk Emails:
           - Mass marketing emails
           - Emails sent to many people simultaneously
           - Promotional content with your name inserted
        
        4. Banking Marketing:
           - Credit card offers
           - Loan offers
           - Insurance promotions
           - Investment opportunities (not actual investments you own)
           - "Extend your banking privileges" type offers
        
        5. Subscriptions and Content:
           - Blog post notifications
           - Publication updates
           - RSS feed emails
           - YouTube channel updates
        
        6. Low-Priority Notifications:
           - "Someone viewed your profile"
           - Forum/community digests
           - Like/comment notifications
           - "See what's new" emails
        
        7. Repetitive Information:
           - Repeated reminders for the same thing
           - Duplicate notifications
           - Follow-up marketing emails
        
        Analyze the email content, sender, and subject carefully.
        For senders, consider if they are a person, company, or automated system.
        For subject, look for action words, personalization, or marketing language.
        For content, examine if it contains specific information for me or is generic.
        
        Answer with ONLY "YES" or "NO" first, followed by a very brief explanation, focusing on the most relevant category that applies.
        """
        
        return prompt
    
    def _parse_necessity_response(self, response_text, email_data):
        """
        Parse the LLM response to determine necessity.
        
        Args:
            response_text (str): Response from LLM
            email_data (dict): Email data for logging purposes
            
        Returns:
            bool: True if necessary, False if unnecessary
        """
        if not response_text:
            logger.warning(f"Empty response for email: {email_data.get('subject', '(No Subject)')}")
            return True
        
        # Get first word of response
        first_word = response_text.split()[0].upper() if response_text.split() else ""
        
        if first_word == "YES":
            logger.debug(f"Email deemed necessary: {email_data.get('subject', '(No Subject)')}")
            return True
        elif first_word == "NO":
            logger.debug(f"Email deemed unnecessary: {email_data.get('subject', '(No Subject)')}")
            return False
        else:
            # If response is ambiguous, look for YES/NO in the first line
            first_line = response_text.split('\n')[0].upper() if '\n' in response_text else response_text.upper()
            
            if "YES" in first_line and "NO" not in first_line:
                logger.debug(f"Email deemed necessary (ambiguous response): {email_data.get('subject', '(No Subject)')}")
                return True
            elif "NO" in first_line and "YES" not in first_line:
                logger.debug(f"Email deemed unnecessary (ambiguous response): {email_data.get('subject', '(No Subject)')}")
                return False
            else:
                # Default to keeping email if truly ambiguous
                logger.warning(f"Ambiguous response for email: {email_data.get('subject', '(No Subject)')}. Defaulting to necessary.")
                logger.warning(f"Response was: {response_text}")
                return True