const { parseProxyData, parseProxyHeader } = require('../lib/proxy');

const BUFFER = Buffer.from(
  '0d0a0d0a000d0a515549540a2111001aac190001ac1900c8b570276805000b74776f7475'
   + '62652e636f6d474554202f20485454502f312e310d0a686f73743a2074776f7475626'
   + '52e636f6d3a31303038380d0a63616368652d636f6e74726f6c3a206d61782d616765'
   + '3d300d0a757067726164652d696e7365637572652d72657175657374733a20310d0a7'
   + '57365722d6167656e743a204d6f7a696c6c612f352e3020285831313b204c696e7578'
   + '207838365f363429204170706c655765624b69742f3533372e333620284b48544d4c2'
   + 'c206c696b65204765636b6f29204368726f6d652f39382e302e343735382e31303220'
   + '5361666172692f3533372e33360d0a6163636570743a20746578742f68746d6c2c617'
   + '0706c69636174696f6e2f7868746d6c2b786d6c2c6170706c69636174696f6e2f786d'
   + '6c3b713d302e392c696d6167652f617669662c696d6167652f776562702c696d61676'
   + '52f61706e672c2a2f2a3b713d302e382c6170706c69636174696f6e2f7369676e6564'
   + '2d65786368616e67653b763d62333b713d302e390d0a7365632d6770633a20310d0a6'
   + '163636570742d656e636f64696e673a20677a69702c206465666c6174650d0a616363'
   + '6570742d6c616e67756167653a20656e2d55532c656e3b713d302e390d0a0d0a',
  'hex'
);

describe('PROXY PROTOCOL handling', () => {
  it('can decode v2', () => {
    const header = parseProxyHeader(BUFFER.subarray(0, 16));
    const data = parseProxyData(header, BUFFER.subarray(16, 16 + header.length));
    console.log(data);
  });
});
