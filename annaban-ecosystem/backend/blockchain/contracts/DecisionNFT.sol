// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract DecisionNFT is ERC721, Ownable {
    uint256 public nextTokenId;

    struct DecisionMeta {
        string decisionHash;
        uint256 timestamp;
        uint256 confidenceBps;
        uint256 ethicalBps;
    }

    mapping(uint256 => DecisionMeta) public metadataByToken;

    constructor() ERC721("AnnabanDecision", "ABDEC") Ownable(msg.sender) {}

    function mintDecision(
        address to,
        string memory decisionHash,
        uint256 confidenceBps,
        uint256 ethicalBps
    ) public onlyOwner returns (uint256) {
        uint256 tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        metadataByToken[tokenId] = DecisionMeta(decisionHash, block.timestamp, confidenceBps, ethicalBps);
        return tokenId;
    }
}
