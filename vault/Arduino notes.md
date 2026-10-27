
Lectures will have discussions sprinkled in.

- Electricity involves electric charges, which can build up or flow.
- Electrons are negative (−), protons are positive (+). Opposite charges attract, similar charges repel.
- Static electricity = a buildup of electric charge. Ex: a charged balloon sticks to a neutral wall because it slightly shifts the charges in the wall.
- Potential energy = stored energy due to position or arrangement. Separated charges can store electrical potential energy.
- Lightning = a sudden electrical discharge that releases stored energy as light, heat, and sound.

- Voltage (V) = the difference in electrical potential between 2 points, measured in volts. Think of it as the electrical push.
- Ex: a 5 V battery has a 5-volt difference between its terminals.
- Current (I) = how much electric charge flows past a point each second, measured in amperes (A), or amps.
- Coulomb (C, pronounced “koo-lom”) = a unit of electric charge. 1 amp = 1 coulomb per second.
- 1,000 milliamps (mA) = 1 amp.
- River example: voltage = height difference between the lakes; current = amount of water passing each second; resistance = restrictions in the water’s path.

- Direct current (DC) flows in one direction, ex: battery-powered circuits. Its amount can change over time.
- Alternating current (AC) repeatedly reverses direction.
- Wall outlets supply AC. Arduino circuits run on DC.

- Resistance (R) = how much something opposes current, measured in ohms (Ω).
- At the same voltage: more resistance = less current.
- A thicker wire has less resistance than a thinner wire of the same material and length.
- Resistors limit current. Their color bands or markings show their resistance.
- Higher ohms means more resistance. The separate power rating, measured in watts, tells how much heat a resistor can safely dissipate.
- Current flows through all available conducting paths, with more flowing through lower-resistance parallel branches.
- Series circuit = one path, same current through each component.
- Parallel circuit = multiple paths, same voltage across each branch.

Ohm’s law:

- V = I × R
- I = V ÷ R
- R = V ÷ I
- Ohm’s triangle: V on top, I and R underneath. Cover the unknown to find the formula.
- Ex: 5 V across a 1,000 Ω resistor gives 0.005 A = 5 mA.

Arduino circuit basics:

- Closed circuit = a complete path for current. Open circuit = a broken path.
- Short circuit = an unintended low-resistance path that can cause excessive current and damage parts.
- LEDs need current limiting to prevent damage. In our circuits, use a resistor in series with the LED.
- LED polarity matters: the longer leg is usually the anode (+), the shorter leg the cathode (−).
- LED resistor formula: R = (supply voltage − LED forward voltage) ÷ desired current.
- Ex: 5 V supply, 2 V LED drop, and 10 mA current → (5 − 2) ÷ 0.010 = 300 Ω.


- Squiggly lines are PWM pins
- Pulse Width Modulation, or PWM, is a technique for getting analog results with digital means.
- This on-off pattern can simulate voltages in between the full Vcc of the board (e.g., 5V on UNO, 3.3V on a MKR board) and off (0 volts)by changing the portion of the time signal spends on versus the time signal spends off.


- The duration of on time is the pulse width
- To get varying analog values, you can change, or modulate, that pulse width
- PWMS allow us to simulate fractions of voltages from 0-full VCC
- We can set and log signals by writing analogWrite() in our code
- By setting analog write to 0 we are setting our duty cycle to 0%
- By setting it to 255, we are setting it to 100% power.
- Any number in between 0 and 255 is theoretically a fraction of 255

