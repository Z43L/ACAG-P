from typing import Dict, List, Any
import smtplib
from email.mime.text import MIMEText
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class AlertNotifier:
    """Sistema de notificación de alertas para múltiples canales"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.notification_channels = self._setup_channels()
        
    def _setup_channels(self) -> List[Any]:
        """Configura los canales de notificación"""
        channels = []
        
        # Email channel
        if self.config.get('email_enabled', False):
            channels.append(EmailNotifier(self.config.get('email_config', {})))
            
        # Slack channel
        if self.config.get('slack_enabled', False):
            channels.append(SlackNotifier(self.config.get('slack_config', {})))
            
        # PagerDuty channel
        if self.config.get('pagerduty_enabled', False):
            channels.append(PagerDutyNotifier(self.config.get('pagerduty_config', {})))
            
        return channels
        
    def notify_alert(self, alert: Dict[str, Any]) -> bool:
        """Notifica una alerta a través de todos los canales configurados"""
        success = True
        
        for channel in self.notification_channels:
            try:
                channel.notify(alert)
            except Exception as e:
                print(f"Error sending notification via {channel.__class__.__name__}: {str(e)}")
                success = False
                
        return success
        
    def notify_recovery(self, alert: Dict[str, Any]) -> bool:
        """Notifica la recuperación de una alerta"""
        recovery_alert = alert.copy()
        recovery_alert['status'] = 'resolved'
        
        return self.notify_alert(recovery_alert)

class EmailNotifier:
    """Notificador por email"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def notify(self, alert: Dict[str, Any]):
        """Envía notificación por email"""
        msg = MIMEText(self._format_alert_message(alert))
        msg['Subject'] = f"[{alert['severity'].upper()}] {alert['annotations']['summary']}"
        msg['From'] = self.config.get('from_email')
        msg['To'] = ', '.join(self.config.get('to_emails', []))
        
        with smtplib.SMTP(self.config.get('smtp_server')) as server:
            server.login(self.config.get('smtp_user'), self.config.get('smtp_password'))
            server.send_message(msg)
            
    def _format_alert_message(self, alert: Dict[str, Any]) -> str:
        """Formatea el mensaje de alerta"""
        return f"""
        Alert: {alert['annotations']['summary']}
        Description: {alert['annotations']['description']}
        Severity: {alert['severity']}
        Component: {alert['labels']['component']}
        Timestamp: {alert['startsAt']}
        """

class SlackNotifier:
    """Notificador por Slack"""
    
    def __init__(self, config: Dict[str, Any]):
        self.client = WebClient(token=config.get('bot_token'))
        self.channel = config.get('channel')
        
    def notify(self, alert: Dict[str, Any]):
        """Envía notificación por Slack"""
        message = self._format_slack_message(alert)
        
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                blocks=self._create_slack_blocks(alert)
            )
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}")
            
    def _format_slack_message(self, alert: Dict[str, Any]) -> str:
        """Formatea mensaje para Slack"""
        status = "🔴 FIRING" if alert['status'] == 'firing' else "✅ RESOLVED"
        return f"{status} {alert['annotations']['summary']}"
        
    def _create_slack_blocks(self, alert: Dict[str, Any]) -> List[Dict]:
        """Crea bloques de formato para Slack"""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Alert: {alert['annotations']['summary']}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Severity:*\n{alert['severity']}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{alert['status']}"},
                    {"type": "mrkdwn", "text": f"*Component:*\n{alert['labels']['component']}"},
                    {"type": "mrkdwn", "text": f"*Started:*\n{alert['startsAt']}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{alert['annotations']['description']}"
                }
            }
        ]