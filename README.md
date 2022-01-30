# Collection of Vyper contracts

This is a collection of smart contracts implemented in the Vyper smart contract language on Ethereum.

CAUTION: Not meant for production use.

# Dependencies

For Vyper contracts:
- [Vyper](https://github.com/vyperlang/vyper)
- [Brownie](https://github.com/eth-brownie/brownie)

For Cairo contracts:
- [Cairo](https://www.cairo-lang.org/docs/quickstart.html)
- [Starknet](https://www.cairo-lang.org/docs/hello_starknet/account_setup.html#installation)

# Directory

- `ERC721.vy`: ERC-721 implementation with ERC721Metadata, ERC721Enumerable and ERC721Receiver interfaces
- `PlainEIP712.vy`: Simple implementation of EIP712, with reference to [Yearn Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy)
- `EIP4494.vy`: `ERC721.vy` with implementation of EIP-4494 (approval for transfer by signature).
- `VickreyAuction.vy`: A simple Vickrey auction (winning bidder pays second highest bid).
- `VickreyAuctionERC721.vy`: Extension of `VickreyAuction.vy` with ERC-721 non-fungible token held in escrow by auction contract.
- EIP-4671
	- `NTT.vy`: Implementation of EIP-4671 Non-Tradable Token Standard.
	- `NTTDelegate.vy`: Implementation of EIP-4671 Non-Tradable Token Standard with
		delegation and batch minting.
- StarknetDeposit: Vyper implementation of a modified Starknet's L1-L2 (bridge)[https://www.cairo-lang.org/docs/hello_starknet/l1l2.html] for ERC-20. See `README.md` in folder for more details.

# Testing

Run `brownie test` in your console.
