## V0.95 - Solid Progress



#### Added:

* Support for basic SRBs
* An additional default rocket family with SRBs

#### Changed:

* Manual rocket data entry is disabled, it may come back, or may not
* JSON fields have been changed slightly, manStage is now man\_stage\_add, because it is clearer in purpose but most importantly, it actually follows snake\_case convention which was annoying me, a lot. This change is backwards compatible, manStage still works.
* Manual stage addition is no longer carried throughout the program, it is checked at the start of the program and if true, it converts it to separate stages. This will save me a lot of headaches long term.
* Codebase was refactored to consistently follow pep8.

#### Fixed:

* Fuel reserve system was wrong, it was doubly penalising the payload capacity, effectively making the reserve double what was intended.

## V0.90 - MECO

#### Added:

* Stage by stage breakdown for dV, so you know when staging actually occurs and which stages provide how much energy.
* Added config.py, adding a way for users to customise RPAT a little bit, including modifting step rates for calculations, toggling the new dark mode, enabling debug mode or even disabling the graph. This may eventually just get ported to a more industrially standard .cfg file, but it will do for now!
* ANSI colour support in the terminal, to make it more readable.

#### Changed:
* Completely changed the architecture of the application, it is now more organised into a proper structure


## V0.85 - Bingo Fuel

#### Added:

* Fuel reserve system added to the \_rocket.json files.
* Automatic conversion of the reserve fuel to penalty mass in user\_inputs.py.
* RPAT now uses the mass adjusted for reserves to calculate payload capacity.
* Added a new curve to the graph for recoverable rockets, showing delta V penalty of recovery. This is detected automatically based upon the fuel reserve
*Dark mode!


#### Changed:

* The way RPAT.py generates the graphs has been refactored to support the new curve, it is now a separate helper function.
* Graphs have been further refined to make them a bit clearer to the user, outside of debug mode.


#### Notes:

Although fuel_reserves has been added as a variable to a default rocket (falcon 9), it does not need to be added for RPAT to work, if you do not include this variable, it is generated as an empty array and will not impact the calculations or graphs. Overall, this feature was designed to make RPAT compatible with propulsively recovered rockets, and to support fuel residuals. It is not completely without fault, but it is a good estimation if you can find the data on the rocket.


## V0.75 - Movement

#### Changed:

* Separated rockets.json into custom\_rockets.json \& default\_rockets.json
* Improved the comments in rpat.py to make the code more transparent
* Slightly improved error handling in rpat.py
* Modified user\_input.py to accommodate the newest changes to rocket loading
* Separated trajectory\_targets into a new json file, so that they can be more easily modified



### Notes:

You must now port any of your custom rockets into the custom\_rockets.json BEFORE updating, this will prevent your custom

rockets from being overwritten.

This update means that future expansions of default rockets will not impact your custom rockets, from now on, custom\_rockets.json

in the repo will remain as-is, you are free to modify that file in your own copy without fear of it being replaced (as long as you don't

copy the file from the repo into your own).


## V0.65 - Tweaking

### Changed:

* Minor tweaks and fixes from V0.6.
* Actually removed sub-orbital parameters.
* Improved graph scaling outside of debug mode.

## V0.6 - Expansionism

### Added:

* Improvements to the manual and preset input system in the terminal.
* Massive expansion of the rockets library.
* Entirely new metric, HEQ, based off the new integral calculations.
* Selected rocket names to the relevant graphs, and to the terminal.
* Generic .gitignore file that should cover all the bases.


### Changed:

* Completely removed /Example Scripts as the purpose of it is now defunct.
* Completely removed PEQ/NPEQ metrics, as they have been made redundant.
* Changed MIPEQ metric into the LEQ metric, for better understanding and readability.
* Added \*some\* sources to the rockets.txt lookup table.
* Changed some things around in the terminal and fixed a few minor printing issues
* Completely rewrote README.md for the new metrics, as well as to make it easier to read and understand
* Removed sub-orbital parameters from trajectory\_targets as sub-orbital trajectories are incompatible with the integral calculations for HEQ.


### Notes:

rockets.json is subject to being reworked in the future, any custom additions of it will need porting to the new system, thus it is highly recommended you utilise the rockets.txt lookup table to store the relevant information for later porting.


## V0.5 - A New Input

### Added

* Terminal based input system created
* Support for manual input for booster-less rockets
* Initial groundwork started for JSON based presets
* Updated README.md


### Notes:

Subsequent updates will NOT include /Example Scripts, this was a placeholder for the json presets before it existed, therefore it will be made redundant with the expansion of rockets.json.


## V0.4

Initial GitHub Release

