const { Telegraf } = require('telegraf');
const { exec } = require('child_process');
const os = require('os');
const process = require('process');

const TOKEN = 'YOUR_BOT_TOKEN'; 
const AUTHORIZED_USER_ID = 123456789; 

const bot = new Telegraf(TOKEN);

bot.start((ctx) => {
  if (ctx.from.id !== AUTHORIZED_USER_ID) {
    ctx.reply("У вас нет прав на использование этого бота.");
    return;
  }

  const keyboard = [
    [{ text: "Включить SSH", callback_data: "enable_ssh" }],
    [{ text: "Выключить SSH", callback_data: "disable_ssh" }],
    [{ text: "Перезагрузить сервер", callback_data: "reboot_server" }],
    [{ text: "Информация о сервере", callback_data: "server_info" }],
  ];

  ctx.reply("Выберите действие:", {
    reply_markup: { inline_keyboard: keyboard },
  });
});

bot.on("callback_query", async (ctx) => {
  if (ctx.from.id !== AUTHORIZED_USER_ID) {
    await ctx.answerCbQuery("У вас нет прав на использование этого бота.");
    return;
  }

  const action = ctx.callbackQuery.data;

  switch (action) {
    case "enable_ssh":
      handleSSH(ctx, "start");
      break;
    case "disable_ssh":
      handleSSH(ctx, "stop");
      break;
    case "reboot_server":
      rebootServer(ctx);
      break;
    case "server_info":
      sendServerInfo(ctx);
      break;
    default:
      ctx.answerCbQuery("Неизвестная команда.");
  }
});

function handleSSH(ctx, action) {
  exec(`sudo systemctl ${action} ssh`, (error, stdout, stderr) => {
    if (error) {
      ctx.editMessageText(`Ошибка при выполнении команды: ${stderr}`);
    } else {
      ctx.editMessageText(`SSH ${action === "start" ? "включен" : "выключен"}.\n${stdout}`);
    }
  });
}

function rebootServer(ctx) {
  exec("sudo reboot", (error, stdout, stderr) => {
    if (error) {
      ctx.editMessageText(`Ошибка при перезагрузке сервера: ${stderr}`);
    } else {
      ctx.editMessageText("Сервер перезагружается.");
    }
  });
}

function sendServerInfo(ctx) {
  const cpuUsage = os.loadavg()[0]; 
  const memory = process.memoryUsage();
  const totalMem = os.totalmem() / (1024 ** 2); 
  const freeMem = os.freemem() / (1024 ** 2); 
  const uptime = formatUptime(os.uptime());

  const info = `
  CPU Загрузка: ${cpuUsage.toFixed(2)}%
  Всего памяти: ${totalMem.toFixed(2)} MB
  Свободно памяти: ${freeMem.toFixed(2)} MB
  Аптайм сервера: ${uptime}
  `;

  ctx.editMessageText(info);
}

function formatUptime(seconds) {
  const days = Math.floor(seconds / (24 * 3600));
  seconds %= 24 * 3600;
  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;
  const minutes = Math.floor(seconds / 60);
  seconds = Math.floor(seconds % 60);

  return `${days} дней, ${hours} часов, ${minutes} минут, ${seconds} секунд`;
}

bot.launch().then(() => {
  console.log("Бот запущен!");
});

process.once("SIGINT", () => bot.stop("SIGINT"));
process.once("SIGTERM", () => bot.stop("SIGTERM"));
