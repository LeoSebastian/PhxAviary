from ethtoken.abi import EIP20_ABI

def get_abi():

    EIP20_ABI.append({
        'constant': True,
        'inputs': [{'name': '','type': 'address'}],
        'name': 'tokenBalance',
        'outputs': [{'name': '','type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    })

    EIP20_ABI.append({
        'constant': True,
        'inputs': [{'name': '_owner','type': 'address'}],
        'name': 'dividends',
        'outputs': [{'name': 'amount','type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    })

    EIP20_ABI.append({
        'constant': False,
        'inputs': [],
        'name': 'reinvestDividends',
        'outputs': [],
        'payable': False,
        'stateMutability': 'nonpayable',
        'type': 'function'
    })

    EIP20_ABI.append({
        'constant': True,
        'inputs': [],
        'name': 'canMine',
        'outputs': [{'name': '', 'type': 'bool'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    })

    EIP20_ABI.append({
        'constant': True,
        'inputs': [],
        'name': 'miningCooldown',
        'outputs': [{'name': '', 'type': 'uint256'}],
        'payable': False,
        'stateMutability': 'view',
        'type': 'function'
    })

    return EIP20_ABI
