if __name__ == '__main__':
    from . import PumpServer
    import argparse

    class ParseAddress(argparse.Action):

        def __call__(self, parser, args, value, option_string=None):
            host, port = value.split(':')
            setattr(args, self.dest, (host, int(port)))

    parser = argparse.ArgumentParser(description='Run New Era pump server')
    parser.add_argument('address', action=ParseAddress, default=('', 13131))
    args = parser.parse_args()
    PumpServer(address=args.address).run_forever()
