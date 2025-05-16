declare namespace jest {
  interface Mock {
    (...args: any[]): any;
    mockImplementation: (fn: Function) => Mock;
  }

  function fn(): Mock;
  function mockImplementation(fn: Function): Mock;
}

declare const global: {
  ResizeObserver: jest.Mock;
};
