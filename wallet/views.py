from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from bitcoinlib.services.services import Service
from bitcoinlib.transactions import Transaction
from bitcoinlib.wallets import Wallet as Lib_wallet

from bitcoinlib.services.blockchaininfo import BlockchainInfoClient as BInfo

from .models import Wallet

def _get_tx_type(request, txid, address):
    """A helper function to determine if a tx (transaction)  is credit or debit"""
    service=Service()
    try:
        #get the tx 
        tx=service.gettransaction(txid)
        #convert the tx object to a dictionary
        dict=tx.as_dict()
        inputs=dict['inputs']
        
        for input in inputs:
            prev_txid=input['prev_txid']
            prev_t=service.gettransaction(prev_txid)
            dict2=prev_t.as_dict()
            outputs=dict2['outputs']
            for output in outputs:
                sender_address=output['address']
                break
            break
                
        if sender_address==address:
            return 'Sent'
        else:
            return 'Received'
    except AttributeError:
        #incase of coinbase tx
        return 'Received'
    
@login_required
def dashboard(request):
    """the wallet dashboard for a user"""   
    user=request.user
    wallet=Wallet.objects.filter(owner=user)
    user_wallet=wallet[0]
    address=user_wallet.address
    
    #get bitcoinlib service  and wallet bal 
    service=Service()
    wallet_balance=service.getbalance(address)/100000000
    wallet_balance=round(wallet_balance,5)#round tp 2d.p
    
    #PS- divide by 100m above  to convert sat to btc
    
    #get live btc price from api
    base_url=" "
    network="bitcoin"
    denominator='1'
    
    client=BInfo(network=network, base_url=base_url, denominator=denominator)
    
    api_url="https://blockchain.info/tobtc?currency=USD&value=35000"
    num_btc=client.compose_request(api_url)
    """the idea is to get the value of $35,000 in btc and use ratio calcs to get the value of 1 btc in $ """
    btc_price=35000/num_btc
    btc_price=round(btc_price,2)
    
    #wallet bal in $
    wallet_balance_dols= round(wallet_balance*btc_price,2)
    
    #get & process transactions for the user's wallet
    transaction_objects=service.gettransactions(address, limit=6)
    transactions=[  ]
    
    for transaction_object in transaction_objects:
        transaction_detail={ }
        
        dict=transaction_object.as_dict()
        amount=(dict['output_total'] - dict['fee'])/100_000_000
        hash=dict['txid']
        date=dict['date']
        status=dict['status']
        #pack tx details in 1 dict
        transaction_detail['type']= _get_tx_type(request,hash, address)
             
        transaction_detail['amount'] =round(amount,5)
        transaction_detail['hash']=hash
        transaction_detail['date']=date
        transaction_detail['status']=status
        
        transactions.append(transaction_detail)
        transactions.reverse()
        
                        
    context={
        "user":user,
        "user_wallet":user_wallet,
        "wallet_balance":wallet_balance,
        "btc_price":btc_price,
        'transactions':transactions,
        "wallet_balance_dols":wallet_balance_dols
    }
    
    return render(request, 'wallet/dashboard.html',context)

@login_required    
def send_page(request):
    """return the send_page"""
    return render(request, 'wallet/send_page.html')

@login_required
def send(request):
    """send btc to an address provided"""
    if request.method == 'POST':
        
        #get reciever address & amount        
        recipient_address=request.POST.get('recipient_address')
        #remove all whitespace
        recipient_address="".join(recipient_address.split())        
        amount=float(request.POST.get('amount'))
        sat_amount=amount*100_000_000
        
        #retrieve sender  name & wallet 
        user=request.user
        wallet=Lib_wallet(user.username)
        #sent btc
        wallet.send_to(recipient_address,sat_amount, offline=True)
        
        context={ 
            "amount":amount,
            "recipient_address":recipient_address
        }
                        
        return render(request, 'wallet/send_success.html', context)
        