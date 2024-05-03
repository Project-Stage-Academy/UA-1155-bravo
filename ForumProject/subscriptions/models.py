from django.db import models
from startups.models import Startup
from investors.models import Investor


class SubscribeInvestorStartup(models.Model):
    """
    Represents the relationship between an investor and a startup they follow.

    Attributes:
        investor (Investor): The investor following the startup.
        startup (Startup): The startup being followed by the investor.
        saved_at (DateTimeField): The datetime when the investor saved the startup.
    """

    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a string representation of the InvestorStartup instance.

        Returns:
            str: A string representing the investor and startup.
        """
        return f"{self.investor} follows {self.startup}"
