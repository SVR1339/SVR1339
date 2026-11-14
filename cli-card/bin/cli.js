#!/usr/bin/env node

/**
 * svr1339 — Interactive Terminal Business Card
 * Sai Vardhan Reddy · Principal Systems Engineer & Architect
 * Zero dependencies · Runs everywhere in Node.js
 */

const { exec } = require('child_process');
const readline = require('readline');

// ANSI Color Helpers
const RESET = '\x1b[0m';
const BOLD = '\x1b[1m';
const DIM = '\x1b[2m';
const ITALIC = '\x1b[3m';
const UNDERLINE = '\x1b[4m';

// Custom TrueColor / 256 Palette
const BLUE = '\x1b[38;2;47;85;255m';      // #2f55ff Sapphire
const CORAL = '\x1b[38;2;239;59;45m';     // #ef3b2d Coral
const AMBER = '\x1b[38;2;245;158;11m';    // #f59e0b Amber
const WHITE = '\x1b[38;2;245;245;247m';   // Warm White
const GRAY = '\x1b[38;2;134;142;150m';    // Slate Gray
const DARK_GRAY = '\x1b[38;2;73;80;87m';  // Border Gray

const openURL = (url) => {
  const start =
    process.platform === 'darwin' ? 'open' :
    process.platform === 'win32' ? 'start ""' : 'xdg-open';
  exec(`${start} "${url}"`);
};

const CARD = `
${BLUE}┌───────────────────────────────────────────────────────────────────────────┐${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BOLD}${WHITE}SAI VARDHAN REDDY${RESET}  ${DIM}·${RESET}  ${BLUE}@SVR1339${RESET}                                    ${BLUE}│${RESET}
${BLUE}│${RESET}   ${DIM}Principal Systems Engineer · Full-Stack Systems Architect${RESET}               ${BLUE}│${RESET}
${BLUE}│${RESET}   ${CORAL}HIREPAT Ltd.${RESET} ${DIM}· Global Runtimes & Distributed Infrastructure${RESET}             ${BLUE}│${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}├───────────────────────────────────────────────────────────────────────────┤${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BOLD}${WHITE}SYSTEMS ARCHITECTURE MATRIX${RESET}                                             ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}Languages${RESET}     │  ${WHITE}Rust${RESET} · ${WHITE}Python${RESET} · ${WHITE}Go${RESET} · ${WHITE}TypeScript${RESET} · ${WHITE}C++${RESET}                         ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}Runtimes${RESET}      │  ${WHITE}WinTUN Drivers${RESET} · ${WHITE}eBPF Filtering${RESET} · ${WHITE}SIMD${RESET} · ${WHITE}Lock-Free CAS${RESET}      ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}Distributed${RESET}   │  ${WHITE}Zero-Copy Sockets${RESET} · ${WHITE}Fake-IP DoH${RESET} · ${WHITE}Raft Consensus${RESET}         ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}Autonomous${RESET}    │  ${WHITE}Multi-Agent Swarms${RESET} · ${WHITE}Traceback AST Patchers${RESET}             ${BLUE}│${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}├───────────────────────────────────────────────────────────────────────────┤${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BOLD}${WHITE}FEATURED PRODUCTION WORK${RESET}                                                ${BLUE}│${RESET}
${BLUE}│${RESET}   ${AMBER}[1] HidingJackson${RESET}  Sub-ms Global Transparent Proxy Fleet (WinTUN/Rust)  ${BLUE}│${RESET}
${BLUE}│${RESET}   ${AMBER}[2] PRUBETH-CLI${RESET}    Autonomous Multi-Model Engineering Swarm (Python/AGY)${BLUE}│${RESET}
${BLUE}│${RESET}   ${AMBER}[3] HIREPATH-TM${RESET}    High-Concurrency Talent Intelligence Platform        ${BLUE}│${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}├───────────────────────────────────────────────────────────────────────────┤${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BOLD}${WHITE}VERIFIED TOUCHPOINTS${RESET}                                                    ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}[4] Website${RESET}        ${UNDERLINE}https://bsvr.work${RESET}                                      ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}[5] GitHub${RESET}         ${UNDERLINE}https://github.com/SVR1339${RESET}                             ${BLUE}│${RESET}
${BLUE}│${RESET}   ${BLUE}[6] Email${RESET}          contact@bsvr.work                                        ${BLUE}│${RESET}
${BLUE}│${RESET}                                                                           ${BLUE}│${RESET}
${BLUE}└───────────────────────────────────────────────────────────────────────────┘${RESET}
`;

console.log(CARD);

// If running in non-interactive / piped environment (e.g. curl), exit cleanly
if (!process.stdin.isTTY) {
  process.exit(0);
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const promptUser = () => {
  rl.question(
    ` ${BOLD}${BLUE}Select an action [1-5]${RESET} to open in browser, or ${DIM}[q]${RESET} to exit: `,
    (answer) => {
      const choice = answer.trim().toLowerCase();
      switch (choice) {
        case '1':
          console.log(`\n  ${DIM}Opening HidingJackson...${RESET}`);
          openURL('https://github.com/SVR1339/HidingJackson');
          break;
        case '2':
          console.log(`\n  ${DIM}Opening PRUBETH-CLI...${RESET}`);
          openURL('https://github.com/SVR1339/PRUBETH-CLI');
          break;
        case '3':
          console.log(`\n  ${DIM}Opening HIREPATH-TM...${RESET}`);
          openURL('https://github.com/SVR1339/HIREPATH-TM');
          break;
        case '4':
          console.log(`\n  ${DIM}Opening bsvr.work...${RESET}`);
          openURL('https://bsvr.work');
          break;
        case '5':
          console.log(`\n  ${DIM}Opening GitHub Profile...${RESET}`);
          openURL('https://github.com/SVR1339');
          break;
        case 'q':
        case 'exit':
          console.log(`\n  ${DIM}Thank you for connecting. Have a great day!${RESET}\n`);
          rl.close();
          process.exit(0);
          return;
        default:
          console.log(`  ${DIM}Unrecognized choice. Try 1-5 or q.${RESET}`);
          break;
      }
      setTimeout(promptUser, 600);
    }
  );
};

promptUser();
