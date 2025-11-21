declare module "@jest/globals" {
  export interface Mock {
    (...args: any[]): any;
    mockImplementation: (fn: Function) => Mock;
    mockReturnValue: (value: any) => Mock;
  }

  export function fn(): Mock;
  export function mock(moduleName: string): void;
  export function mock(moduleName: string, factory: () => any): void;
  export function expect(actual: any): any;
  export function describe(name: string, fn: () => void): void;
  export function it(name: string, fn: () => void): void;
  export function beforeEach(fn: () => void): void;
  export function afterEach(fn: () => void): void;
}

declare global {
  var jest: typeof jest;
}
