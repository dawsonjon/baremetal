![build status](https://travis-ci.org/dawsonjon/baremetal.svg?branch=master)

# Baremetal - A simple python utility to describe and simulate hardware in Python

As its name suggests, the baremetal library is intended for circuit design at
a low level of abstraction - think gates and flip-flops. The library was
developed to allow automatic generation of IP blocks.

Even though the abstraction level is very low, it is possible to 
programmatically generate hardware. It is therefore possible to generalise 
designs to a greater extent than is normally possible in an HDL. One of the key
goals is to allow algorithms to be generalised to different data types for
example writing FFT code that works with fixed or floating point types.

The library offers a capability to natively simulate IP allowing unit-tests
to be quickly and easily written in Python without relying on any dependencies.
The simulation model is different than a typical HDL simulator that uses events
and delta-cycles to model the propagation of signals through asynchronous logic.
Instead, the value of each net is generated at the point it is needed.
Synchronous circuit nets are updated once at reset and at each clock edge. 

The library has the capability to output code in verilog so that it can be
verified using a traditional verilog simulator, or synthesised. At present, 
the code is very much biased towards FPGAs.

install:

```
	git clone https://github.com/dawsonjon/baremetal.git
	cd baremetal
	sudo python3 setup.py install
```
