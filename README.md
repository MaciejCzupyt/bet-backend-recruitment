# Zadanie: API do zarządzania adresami dostaw i produktami w zamówieniu

- **Order.address**: Reprezentuje domyślny adres klienta.
- **Model Logistic**: Odpowiada za wysyłkę produktów do klienta.

Zdarza się, że klient kontaktuje się z nami z prośbą o wysyłkę części produktów na inny adres.

# Changelog

- Added serializers.py for split shipment request validation and serialization

- Implemented the split_shipment endpoint, including:
  - robust error handling
  - transactional concurrency support
  - handling of certain edge cases
- Introduced the OperationLog model and added constraints to existing models
- Added comprehensive test coverage with new tests and fixtures