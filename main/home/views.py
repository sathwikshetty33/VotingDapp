from datetime import datetime, timedelta
import json
import logging
import time
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3
from django.shortcuts import render

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VotingContractHandler:
    def __init__(self):
        try:
            self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_URL))
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Ethereum network")

            # Load contract ABI and create contract instance
            with open(r"C:\Users\Sathw\OneDrive\Desktop\bc\main\home\abi.json", 'r') as f:
                contract_abi = json.load(f)

            self.contract = self.w3.eth.contract(
                address=settings.CONTRACT_ADDRESS,
                abi=contract_abi
            )

        except Exception as e:
            logger.error(f"Contract initialization error: {e}")
            raise

    def validate_registration_data(self, name, age, gender):
        if not name or not isinstance(name, str):
            raise ValueError("Invalid name")
        if not isinstance(age, int) or age < 18:
            raise ValueError("Invalid age")
        if not gender or gender not in ['Male', 'Female', 'Other']:
            raise ValueError("Invalid gender")

    def register_candidate(self, name, party, age, gender, user_address):
        try:
            self.validate_registration_data(name, age, gender)
            tx_hash = self.contract.functions.candidateRegister(
                name, party, age, gender
            ).transact({'from': user_address})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'success': True,
                'transaction_hash': tx_receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Candidate Registration Error: {e}")
            return {'success': False, 'error': str(e)}

    def register_voter(self, name, age, gender, user_address):
        try:
            # Validate input data
            self.validate_registration_data(name, age, gender)

            # Set up transaction parameters with user's address as msg.sender
            tx_hash = self.contract.functions.voterRegister(
                name, age, gender
            ).transact({'from' : user_address})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                'success': True,
                'transaction_hash': tx_receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Voter Registration Error: {e}")
            return {'success': False, 'error': str(e)}

    def cast_vote(self, candidate_id, user_address):
        try:
            if int(candidate_id) < 0:
                raise ValueError("Invalid candidate ID")
            can = int(candidate_id)
            tx_hash = self.contract.functions.Vote(can).transact({'from': user_address})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'success': True,
                'transaction_hash': tx_receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Voting Error: {e}")
            return {'success': False, 'error': str(e)}
    def get_election_result(self):
        try:
            # Find the candidate with the most votes
            candidate_count = self.contract.functions.candidateCount().call()
            max_votes = 0
            winner = None

            for i in range(1, candidate_count + 1):
                candidate_info = self.contract.functions.candidates(i).call()
                if candidate_info[4] > max_votes:
                    max_votes = candidate_info[4]
                    winner = {
                        'id': i,
                        'name': candidate_info[0],
                        'party': candidate_info[1],
                        'votes': candidate_info[4]
                    }

            return {
                'success': True, 
                'winner': winner if winner else None
            }
        except Exception as e:
            logger.error(f"Error fetching election result: {e}")
            return {'success': False, 'error': str(e)}
    def get_candidate(self):
        try:
            # Fetch candidates directly as an array from the contract
            candidates_data = self.contract.functions.candidateLists().call()
            candidates = []
            
            # Process each candidate from the returned array
            for candidate_info in candidates_data:
                try:
                    # Add error checking for each field
                    candidate = {
                        'id': str(len(candidates) + 1),
                        'name': str(candidate_info[0]) if candidate_info[0] else "Unknown",
                        'party': str(candidate_info[1]) if candidate_info[1] else "Unknown",
                        'age': int(candidate_info[2]) if candidate_info[2] else 0,
                        'gender': str(candidate_info[3]) if candidate_info[3] else "Unknown",
                        'votes': int(candidate_info[6])
                    }
                    candidates.append(candidate)
                except (IndexError, TypeError) as e:
                    logger.error(f"Error processing candidate data: {e}")
                    continue
            
            # Return in the exact format your frontend expects
            return JsonResponse({
                'success': True,
                'candidates': candidates
            })
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e),
                'candidates': []  # Always include candidates key even if empty
            })
    def voteTime(self, start_delay, duration, address):
        start_delay_seconds = start_delay * 60
        duration_seconds = duration * 60
            
            # Call the contract method
        tx_hash = contract_handler.contract.functions.voteTime(
            start_delay_seconds,
            duration_seconds
        ).transact({'from': address})
        
        # Wait for transaction receipt
        tx_receipt = contract_handler.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Calculate and format times for display
        start_time = datetime.now() + timedelta(minutes=start_delay)
        end_time = start_time + timedelta(minutes=duration)
        
        return ({
            'success': True,
            'message': 'Voting time set successfully',
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_hash': tx_receipt.transactionHash.hex()
        })
    
contract_handler = VotingContractHandler()


# Views updated to pass user address
@csrf_exempt
@require_http_methods(["POST"])
def register_candidate(request):
    try:
        data = json.loads(request.body)
        user_address = Web3.to_checksum_address(request.COOKIES.get('user_account', ''))
        result = contract_handler.register_candidate(
            data['name'],
            data['party'],
            data['age'],
            data['gender'],
            user_address
        )
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_voter(request):
    try:
        data = json.loads(request.body)
        user_address = Web3.to_checksum_address(request.COOKIES.get('user_account', ''))
        result = contract_handler.register_voter(
            data['name'],
            data['age'],
            data['gender'],
            user_address
        )
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def cast_vote(request):
    try:
        # Parse the JSON data from request
        data = json.loads(request.body)
        candidate_id = data.get('candidate_id')
        
        user_address = Web3.to_checksum_address(request.COOKIES.get('user_account', ''))
        if not user_address:
            return JsonResponse({
                'success': False,
                'error': 'Please connect your wallet first'
            })
        result = contract_handler.cast_vote(candidate_id, user_address)
        # Add this to your voting_status view to debug
        start_time = contract_handler.contract.functions.startTime().call()
        current_time = int(time.time())
        print(f"Start time: {start_time}, Current time: {current_time}")
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Vote cast successfully!',
                'transaction_hash': result['transaction_hash']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error']
            })

    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': 'Invalid input data'
        })
    except Exception as e:
        logger.error(f"Error in cast_vote view: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@require_http_methods(["GET"])
def get_candidates(request):
    try:
        # Initialize your contract instance here
        
        return contract_handler.get_candidate()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'candidates': []
        })


@require_http_methods(["GET"])
def voting_status(request):
    try:    
        current_time = int(time.time())
        end_time = contract_handler.contract.functions.endTime().call()
        stop_voting = contract_handler.contract.functions.stopVoting().call()
        started = contract_handler.contract.functions.started().call()
        startTime = contract_handler.contract.functions.startTime().call()
        if stop_voting:
            message = "Voting has been stopped by admin"
        elif not started:
            message = "Voting has not started yet"
        elif started and current_time < startTime :
             message = "Voting has not started yet"
        elif started and current_time >= end_time:
            message = "Voting period has ended"
        else:
            message = "Voting is open"
            
        return JsonResponse({
            'success': True,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error checking voting status: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Unable to check voting status'
        })


@require_http_methods(["GET"])
def get_result(request):
    winner = contract_handler.get_election_result()
    return JsonResponse({'winner': winner})

@require_http_methods(["GET"])
def logins(request):
    return render(request, 'login.html')
@require_http_methods(["GET"])
def voting(request):
    return render(request, 'voting.html')
def canreg(request):
    return render(request, 'can.html')
def voter(request):
    return render(request, 'voter.html')
@csrf_exempt
def set_vote_time(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_delay = int(data.get('start_delay', 0))  # in minutes
            duration = int(data.get('duration', 0))        # in minutes
            
            user_address = Web3.to_checksum_address(request.COOKIES.get('user_account', ''))
            status = contract_handler.voteTime(start_delay, duration, user_address)
            return JsonResponse({
               'success': status
           })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return render(request, 'admin.html')