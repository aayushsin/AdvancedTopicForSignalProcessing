#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2015.
# Distributed under the "STEINWURF EVALUATION LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import os
import random
import sys

import kodo


def main():
    """
    Encode recode decode example.

    In Network Coding applications one of the key features is the
    ability of intermediate nodes in the network to recode packets
    as they traverse them. In Kodo it is possible to recode packets
    in decoders which provide the recode() function.

    This example shows how to use one encoder and two decoders to
    simulate a simple relay network as shown below (for simplicity
    we have error free links, i.e. no data packets are lost when being
    sent from encoder to decoder1 and decoder1 to decoder2):

            +-----------+     +-----------+     +-----------+
            |  encoder  |+---.| decoder1  |+---.|  decoder2 |
            +-----------+     | (recoder) |     +-----------+
                              +-----------+
    In a practical application recoding can be using in several different
    ways and one must consider several different factors e.g. such as
    reducing linear dependency by coordinating several recoding nodes
    in the network.
    Suggestions for dealing with such issues can be found in current
    research literature (e.g. MORE: A Network Coding Approach to
    Opportunistic Routing).

    
    *********************************************************************
    NOTE:
       This is for the forwarding/recoding example discussed in class
       In the first case H is a recoder and in the second a forwarder!
       S -> R has erasure rate e1 = 80%
       S -> H has erasure rate e2 = 10%
       H -> R has erasure rate e3 = 10%
       The network is like this:

          ---- H ----
         /           \ 
        /             \
       S --------------R

       Can change the encoder and decoder factories to Binary8
       if want to compare with a larger field but it's much slower so
       if you don't want to wait reduce the num_runs.

       DOUBLE CHECK THE RESULTS WITH THEORY!

    *********************************************************************

    """
    # Set the number of symbols (i.e. the generation size in RLNC
    # terminology) and the size of a symbol in bytes
    symbols = 100 #42
    symbol_size = 140 #160
    num_runs = 1000

    # Erasure rates
    e1 = 0.8
    e2 = 0.1
    e3 = 0.1

    # Encoder factory used to build encoder
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(
        max_symbols=symbols,
        max_symbol_size=symbol_size)

    encoder = encoder_factory.build()
    encoder.set_systematic_off()

    # H Recoder case
    # Total packets sent by the source and total number of redundant packets
    total_packets = 0
    total_red_packets = 0
    for i in range(num_runs):

        # Decoder factory used to build recoder and decoder
        decoder_factory = kodo.FullVectorDecoderFactoryBinary(
            max_symbols=symbols,
            max_symbol_size=symbol_size)

        decoder1 = decoder_factory.build()
        decoder2 = decoder_factory.build()

        # Create some data to encode. In this case we make a buffer
        # with the same size as the encoder's block size (the max.
        # amount a single encoder can encode)
        # Just for fun - fill the input data with random data
        data_in = os.urandom(encoder.block_size())

        # Assign the data buffer to the encoder so that we may start
        # to produce encoded symbols from it
        encoder.set_const_symbols(data_in)

        # Packets sent by source and redundant packets for this run
        packets_needed = 0
        red_packets = 0

        past_rank = 0 

        while not decoder2.is_complete():

            # Encode a packet into the payload buffer from the source
            packet = encoder.write_payload()
            packets_needed += 1

            # S -> R direct path
            if random.uniform(0.0,1.0) > e1:
                past_rank = decoder2.rank()
                decoder2.read_payload(packet)
                if decoder2.rank() == past_rank:
                    red_packets += 1

            # The multihop path
            # S -> H where H is a recoder
            if random.uniform(0.0,1.0) > e2:
                decoder1.read_payload(packet)

            # H -> R
            # Not nested in S -> H because sending is independent of receiving in recoder case.
            # i.e. it always sends something out with the info it has already.
            # First produce a new recoded packet from the current
            # decoding buffer, and place it into the payload buffer
            packet = decoder1.write_payload()
            if random.uniform(0.0,1.0) > e3:
                past_rank = decoder2.rank()
                decoder2.read_payload(packet)
                if decoder2.rank() == past_rank:
                    red_packets += 1

        # decoder2 should now be complete,
        # copy the symbols from the decoder
        data_out2 = decoder2.copy_from_symbols()

        # Check we properly decoded the data
        if data_out2 == data_in:
            total_packets += packets_needed
            total_red_packets += red_packets
        else:
            print("Unexpected failure to decode please file a bug report :)")
            sys.exit(1)
    print("Recoder:")
    print("Avg. packets needed:")
    print(total_packets/float(num_runs))
    print("Avg. Redundant packets:")
    print(total_red_packets/float(num_runs))
    print('')

    ########################################################################

    # H Forwarder case
    # Total packets sent by the source and total number of redundant packets
    total_packets = 0
    total_red_packets = 0
    for i in range(num_runs):

        # Decoder factory used to build recoder and decoder
        decoder_factory = kodo.FullVectorDecoderFactoryBinary(
            max_symbols=symbols,
            max_symbol_size=symbol_size)

        decoder1 = decoder_factory.build()
        decoder2 = decoder_factory.build()

        # Create some data to encode. In this case we make a buffer
        # with the same size as the encoder's block size (the max.
        # amount a single encoder can encode)
        # Just for fun - fill the input data with random data
        data_in = os.urandom(encoder.block_size())

        # Assign the data buffer to the encoder so that we may start
        # to produce encoded symbols from it
        encoder.set_const_symbols(data_in)

        # Packets sent by source and redundant packets for this run
        packets_needed = 0
        red_packets = 0

        past_rank = 0 

        while not decoder2.is_complete():

            # Encode a packet into the payload buffer from the source
            packet = encoder.write_payload()
            packets_needed += 1

            # S -> R direct path
            if random.uniform(0.0,1.0) > e1:
                past_rank = decoder2.rank()
                decoder2.read_payload(packet)
                if decoder2.rank() == past_rank:
                    red_packets += 1

            # The multihop path
            # S -> H where H is a recoder
            if random.uniform(0.0,1.0) > e2:
                decoder1.read_payload(packet)

                # H -> R
                # Only get to this point if S -> H succeeds
                # It's going to be the same packet from the encoder since
                # just forwarding here!
                if random.uniform(0.0,1.0) > e3:
                    past_rank = decoder2.rank()
                    decoder2.read_payload(packet)
                    if decoder2.rank() == past_rank:
                        red_packets += 1

        # decoder2 should now be complete,
        # copy the symbols from the decoder
        data_out2 = decoder2.copy_from_symbols()

        # Check we properly decoded the data
        if data_out2 == data_in:
            total_packets += packets_needed
            total_red_packets += red_packets
        else:
            print("Unexpected failure to decode please file a bug report :)")
            sys.exit(1)
    print("H Forwarder:")
    print("Avg. packets needed:")
    print(total_packets/float(num_runs))
    print("Avg. Redundant packets:")
    print(total_red_packets/float(num_runs))


if __name__ == "__main__":
    main()
