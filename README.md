PHX Aviary Alpha v0.2\
Released 19th March, 2018
\
Created by: Mr Fahrenheit, Norsefire\
\
Implemented in Python. Confirmed working on Python 3.6. Aviary is NOT Python 2.7 compatible.\
We recommend using Anaconda and creating a new environment.\
\
Required dependencies/packages (for Windows):\
python -m pip install ethtoken web3==4.00-beta.11\
\
For Windows you will also need to install this: http://landinghub.visualstudio.com/visual-cpp-build-tools\
(Only if you receive an error about Visual C++ 14.0 being required when installing the packages above)\
\
This program has not yet been tested with OSX or Linux, so let us know if you have any issues with using it on either.\
\
Simply modify your config file, run the program (python phx_aviary.py), and leave it alone.\
\
This program supports more than one wallet in your config file. For example:\
\
[main_wallet]\
pub_key  = (public_key_1)\
priv_key = (private_key_1)\
mine_only = 0\
\
[wallet_for_my_pet_phoenix]\
pub_key  = (public_key_2)\
priv_key = (private_key_2)\
mine_only = 1\
\
Any feedback or suggestions, reach either of us on the EthPhoenix Discord, or via:\
Mr Fahrenheit: coins@leosebastian.com\
Norsefire: norsefire_phx@protonmail.com
