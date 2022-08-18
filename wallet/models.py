from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    """A wallet that belongs to a user"""
    private_key=models.CharField(max_length=300)
    public_key=models.CharField(max_length=300)
    address=models.CharField(max_length=300)
    owner=models.ForeignKey(User, on_delete=models.CASCADE, related_name="owns")
    
    def  __str__(self):
        """Return a string representation of the wallet"""
        return self.owner.username
        
    
    