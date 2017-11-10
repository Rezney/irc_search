from django.db import models


class IRCMessage(models.Model):
    
    irc_channel = models.CharField(max_length=49)
    date = models.DateTimeField(db_index=True)
    nick = models.CharField(max_length=50)
    message = models.TextField()

    class Meta:
        unique_together = ["nick", "message", "date"]
        index_together = [['irc_channel', 'date']]

    def __str__(self):
        return '%s/%s' % (self.message_id, self.irc_channel)
