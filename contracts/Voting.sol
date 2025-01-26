// SPDX-License-Identifier: MIT

pragma solidity >=0.7.0 <0.9.0;

contract Voting{
    struct Voter{
        string name;
        uint age;
        uint voterId;
        string gender;
        uint voteCandidateId;
        address voterAddress;
    }
    struct Candidate{
        string name;
        string party;
        uint age;
        string gender;
        uint candidateId;
        address candidateAddress;
        uint votes;
    }
    address eletionCommission;
    address public winner;
    uint nextVoterId=1;
    uint nextCandidateId=1;
    uint startTime;
    uint endTime;
    mapping(uint=> Voter) voterDetails;
    mapping(uint=> Candidate) candidateList;
    bool stopVoting;
    constructor(){
        eletionCommission=msg.sender;
        startTime = block.timestamp;
        endTime = block.timestamp + 600;
    }
    modifier onlyCommision(){
        require(msg.sender==eletionCommission,"You are unautjorized");
        _;
    }
    function candidateRegister(string calldata name, string calldata party, uint age, string calldata gender ) external 
    {
        require(age>=18,"You are underage");
        require(block.timestamp < startTime,"Voting already started cannot registered");
        require(candidateVerification(msg.sender)==true,"You have already registered");
        // require(nextCandidateId<3,"Already Filled");
        candidateList[nextCandidateId]=Candidate(name,party,age,gender,nextCandidateId,msg.sender,0);
        nextCandidateId++;
    }
    function candidateVerification(address ad) internal view returns (bool){
        for(uint i=1;i<nextCandidateId;i++)
        {
            if(ad==candidateList[i].candidateAddress)
            {
                return false;
            }
        }
        return true;
    }
    function candidateLists() public  view returns(Candidate[] memory){
        Candidate[] memory can=new Candidate[](nextCandidateId-1);
        for(uint i=1;i<nextCandidateId;i++)
        {
           can[i-1]=candidateList[i];
        }
        return can;
    }
    function voterRegister(string calldata name,  uint age, string calldata gender ) external 
    {
        require(age>=18,"You are underage");
        require(voterVerification(msg.sender)==true,"You have already registered");
        // require(nextCandidateId<3,"Already Filled");
        voterDetails[nextVoterId]=Voter(name,age,nextVoterId,gender,0,msg.sender);
         nextVoterId++;
    }
    function voterVerification(address ad) internal view returns (bool){
        for(uint i=1;i<nextVoterId;i++)
        {
            if(ad==voterDetails[i].voterAddress)
            {
                return false;
            }
        }
        return true;
    }
   function voterLists() public  view returns(Voter[] memory){
        Voter[] memory can=new Voter[](nextVoterId-1);
        for(uint i=1;i<nextVoterId;i++)
        {
           can[i-1]=voterDetails[i];
        }
        return can;
    }
    function Vote(uint id) public {
        require(voterVerification(msg.sender)==false,"You have not registered");
        require(VoterId(msg.sender)!=0,"You have already Voted");
        require(block.timestamp<endTime && stopVoting==false," voting period over");
        require(id > 0 && id < nextVoterId,"Enter the correct Id");
        voterDetails[VoterId(msg.sender)].voteCandidateId = id;
        candidateList[id].votes++;
    }
    function VoterId(address ad) internal view returns(uint) {
        for(uint i=1;i<nextVoterId;i++)
        {
            if(ad==voterDetails[i].voterAddress)
            {
                if(voterDetails[i].voteCandidateId == 0){
                    return i;
                }
                else {
                    return 0;
                }
            }
        }
        return 0;
    }
    function Result() external onlyCommision(){
        require(block.timestamp>=endTime," voting period not over");
        uint max=0;
        for(uint i=1;i<nextCandidateId;i++)
        {
           if(candidateList[i].votes>max)
           {
            max=candidateList[i].votes;
            winner = candidateList[i].candidateAddress;
           }
        }
    }
    function voteTime(uint start,uint duration) external onlyCommision() {
        startTime=start;
        endTime=startTime + duration;
    }
    function votingStatus() view external returns(string memory){
            if(startTime==0){
                return "Voting not Started";
            }
            else if((endTime > block.timestamp) || !stopVoting){
                return "Voting under Progress";
            }
            else{
                return "Voting has ended";
            }
    }
    function emergency() external onlyCommision() {
        stopVoting=true;
    }

}