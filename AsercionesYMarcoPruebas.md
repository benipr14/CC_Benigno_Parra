# Biblioteca de aserciones y marco de pruebas
Para la biblioteca de aserciones se ha decidido hacer uso de las aserciones de pytest, ya que permite hacer uso de una sintaxis simple 'assert', la cual muestra informes claros cuando falla. También permite el uso de 'pytest.approx' que facilita la comparación de floats con tolerancia, además es muy utilizado en la actualidad por lo que me será fácil encontrar soluciones y me encuentro con algún problema.

El enfoque es mas cercano a TDD, ya que utiliza asserts directos y fixtures y las funciones son pequeñas con comprobaciones precisas.

Para el test runner se hará uso también de pytest, ya que detecta tests automáticamente por convención de nombres, soporta fixtures, inyecta mongomock (necesario para la base de datos en los tests), parametrización y plugins. Además, ya lo tenía en uso para las aserciones por lo que utilizarlo de nuevo me sería más fácil.