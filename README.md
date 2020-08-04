# Wallets

Небольшое приложение простой платежной системы на aiohttp и postgresql.

## Запуск
docker-compose up -d

## Юнит-тесты
docker exec -ti wallets_web pytest backend/tests

## API
**Создание юзера и кошелька**
```
POST /api/user/register/ {'name': str, 'password': str}
```
*По умолчанию создается кошелек в валюте USD*

**Логин**
```
POST /api/user/login/ {'name': str, 'password': str}
```

**Логаут**
```
POST /api/user/logout/ {}
```

**Пополнить кошелек**
```
POST /api/wallet/top-up/ 
{
    'value': str  // сумма пополнения,
    'currency': str  // валюта пополнения, доступно только значение 'USD'
    'trx_code': str  // код идемпотентности
}
```

**Перевести деньги другому участнику**
```
POST /api/wallet/transfer/
{
    'name_to': str  // имя юзера в системе
    'value': str  // сумма перевода
    'currency': str  // валюта перевода, доступна только 'USD'
    'trx_code': str  // код идемпотентности
}
```