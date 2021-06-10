from concurrent import futures
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend


class EmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        super(EmailBackend, self).__init__(*args, **kwargs)

        self.executor = futures.ThreadPoolExecutor(
                max_workers=int(getattr(settings, 'EMAIL_BACKEND_POOL_SIZE', 15))
        )

    def send_messages(self, email_messages):
        return self.executor.submit(super().send_messages, email_messages)
