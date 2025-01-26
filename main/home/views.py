import json
import logging
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
            # Initialize Web3 connection
            self.w3 = Web3(Web3.HTTPProvider(settings.BLOCKCHAIN_URL))

            # Validate Web3 connection
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
            if not isinstance(candidate_id, int) or candidate_id < 0:
                raise ValueError("Invalid candidate ID")
            
            tx_hash = self.contract.functions.vote(candidate_id).transact({'from': user_address})
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return {
                'success': True,
                'transaction_hash': tx_receipt.transactionHash.hex()
            }
        except Exception as e:
            logger.error(f"Voting Error: {e}")
            return {'success': False, 'error': str(e)}

    def get_voting_status(self):
        try:
            # Assuming your contract has a method to check voting status
            status = self.contract.functions.votingOpen().call()
            return {'success': True, 'status': status}
        except Exception as e:
            logger.error(f"Error checking voting status: {e}")
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
            # Fetch candidates from the contract
            candidate_count = self.contract.functions.candidateList().call()
            candidates = []
            
            for i in range(1, candidate_count + 1):
                candidate_info = self.contract.functions.candidates(i).call()
                candidates.append({
                    'id': i,
                    'name': str(candidate_info[0]),  # Ensure string conversion
                    'party': str(candidate_info[1]),
                    'age': int(candidate_info[2]),
                    'gender': str(candidate_info[3]),
                    'votes': int(candidate_info[4])
                })
            
            return {'success': True, 'candidates': candidates}
        except Exception as e:
            logger.error(f"Error getting candidates: {e}")
            return {'success': False, 'error': str(e)}
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
        data = json.loads(request.body)
        user_address = Web3.to_checksum_address(request.COOKIES.get('user_account', ''))

        result = contract_handler.cast_vote(
            data['candidate_id'],
            user_address
        )
        return JsonResponse(result)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing key: {str(e)}'}, status=400)

@require_http_methods(["GET"])
def get_candidates(request):
    candidates = contract_handler.get_candidate()
    return JsonResponse({'candidates': candidates})


@require_http_methods(["GET"])
def voting_status(request):
    status = contract_handler.get_voting_status()
    return JsonResponse({'status': status})


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
