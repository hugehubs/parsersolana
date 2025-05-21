import asyncio
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import base64 # Может понадобиться для декодирования сырых данных

# Константы
RPC_URL = "https://solana-rpc.publicnode.com"
MARKET_ACCOUNT_ADDRESS = Pubkey.from_string("GQsPr4RJk9AZkkfWHud7v4MtotcxhaYzZHdsPCg9vNvW")
TRUMP_MINT = Pubkey.from_string("6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN") # Лучше использовать Pubkey для сравнения
WSOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112") # Лучше использовать Pubkey для сравнения

async def get_market_raw_data():
    """
    Получает сырые данные непосредственно из аккаунта Raydium Market.
    """
    async with AsyncClient(RPC_URL) as client:
        # Используем get_account_info для получения данных самого аккаунта
        # Убираем encoding="jsonParsed", чтобы получить сырые данные
        resp = await client.get_account_info(
            MARKET_ACCOUNT_ADDRESS,
            # encoding="base64" # base64 это кодировка по умолчанию для сырых данных
        )

        if not resp.value:
            print(f"Ошибка: Аккаунт {MARKET_ACCOUNT_ADDRESS} не найден.")
            return None

        # resp.value.data теперь содержит сырые данные аккаунта
        # Обычно это список [base64_string, encoding_type]
        raw_data_encoded = resp.value.data

        if isinstance(raw_data_encoded, list) and raw_data_encoded[1] == 'base64':
            raw_data_bytes = base64.b64decode(raw_data_encoded[0])
            print(f"Получены сырые данные аккаунта ({len(raw_data_bytes)} байт).")
            # print("Первые 50 байт сырых данных:", raw_data_bytes[:50]) # Для отладки
            return raw_data_bytes
        else:
             print("Неожиданный формат сырых данных:", raw_data_encoded)
             return None


async def get_trump_price():
    """
    Пытается получить цену TRUMP в WSOL, декодируя сырые данные Market Account.
    """
    while True:
        try:
            raw_data = await get_market_raw_data()

            if raw_data:
                # --- САМАЯ СЛОЖНАЯ ЧАСТЬ ---
                # Здесь вам нужно вручную декодировать `raw_data` (объект bytes)
                # согласно структуре данных Raydium Concentrated Liquidity Market Account.
                # Raydium использует сложную структуру данных для своих пулов.
                # Чтобы извлечь резервы WSOL и TRUMP, нужно знать смещения (offsets)
                # и типы данных в этих байтах.

                # К сожалению, я не могу предоставить код для декодирования структуры Raydium Market Account,
                # так как это требует специфических знаний Raydium Program или их SDK.
                # Это не простое чтение полей.

                # Например, если бы резервы были просто двумя uint64 на известных смещениях:
                # import struct
                # try:
                #     # Примерные смещения и форматы - НЕВЕРНО для Raydium Market!
                #     wsol_reserve_raw = struct.unpack_from("<Q", raw_data, offset=reserve1_offset)[0]
                #     trump_reserve_raw = struct.unpack_from("<Q", raw_data, offset=reserve2_offset)[0]
                #     # Вам также нужны десятичные знаки, которые тоже хранятся где-то в данных
                #     wsol_decimals = ... # Извлечь из данных или знать заранее
                #     trump_decimals = ... # Извлечь из данных или знать заранее
                #
                #     wsol_reserve = wsol_reserve_raw / (10 ** wsol_decimals)
                #     trump_reserve = trump_reserve_raw / (10 ** trump_decimals)
                #
                #     if trump_reserve > 0 and wsol_reserve > 0:
                #         price = wsol_reserve / trump_reserve
                #         print(f"💰 Цена TRUMP: {price:.8f} WSOL (по сырым резервам)")
                #     else:
                #         print("⚠️ Резервы TRUMP или WSOL в сырых данных нулевые.")
                # except Exception as decode_error:
                #     print(f"❌ Ошибка при декодировании сырых данных: {decode_error}")
                #     print("Проверьте логику декодирования и смещения.")

                print("⚠️ Получены сырые данные аккаунта Raydium Market, но их декодирование требует специфических знаний структуры данных Raydium.")
                print("Не удалось рассчитать цену по сырым данным без логики декодирования Raydium.")

            else:
                # Это произойдет, если get_market_raw_data вернула None
                pass # Сообщение об ошибке уже выводится внутри get_market_raw_data

        except Exception as e:
            print(f"❌ Произошла ошибка в основном цикле: {e}")
            # print(f"Тип ошибки: {type(e).__name__}") # Для отладки

        await asyncio.sleep(5) # Пауза между запросами

if __name__ == "__main__":
    # Убедитесь, что у вас установлена библиотека solana: pip install solana
    # Убедитесь, что вы запускаете скрипт с правильным интерпретатором Python
    asyncio.run(get_trump_price())