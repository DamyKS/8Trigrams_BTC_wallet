from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

from bitcoinlib.keys import Key
from bitcoinlib.wallets import Wallet

from wallet.models import Wallet as Custom_Wallet

def register(request):
	"""Register a new user."""
	if request.method != 'POST':
		# Display blank registration form.
		form = UserCreationForm()
	else:
		# Process completed form.
		form = UserCreationForm(data=request.POST)
		
		if form.is_valid():
			#create new user
			new_user = form.save()
			
			#create new custom wallet
			new_wallet=Custom_Wallet()
			
			#create bitcoin new key
			new_key=Key()
			
			#get the new private & public keys and the new address
			private_key=new_key.private_hex
			public_key=new_key.public_hex
			address=new_key.address()
			
			#add the 3 info above to the cutsom wallet
			new_wallet.private_key=private_key
			new_wallet.public_key=public_key
			new_wallet.address=address
			new_wallet.owner=new_user
			
			#save the new wallet
			new_wallet.save()
			#create bitcoinlib wallet with user details
			Wallet.create(new_user.username, keys=private_key, scheme="single")
			
			# Log the user in and then redirect to home page.
			login(request, new_user)
			return redirect('wallet:dashboard')
	
	# Display a blank or invalid form.
	context = {'form': form}
	return render(request, 'registration/register.html', context)
		
