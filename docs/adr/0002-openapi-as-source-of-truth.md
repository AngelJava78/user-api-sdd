# ADR-0002 — OpenAPI como contrato HTTP

## Estado

Propuesto

## Contexto

La API debe desarrollarse mediante Spec-Driven Development.

## Decisión

El contrato OpenAPI será la referencia principal para endpoints, parámetros, payloads y respuestas HTTP.

## Consecuencias

Cualquier cambio de API debe comenzar actualizando el contrato y sus criterios de aceptación antes de modificar la implementación.
