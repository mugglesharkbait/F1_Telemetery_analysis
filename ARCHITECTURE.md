# Architecture Overview

## 🏗️ Refactored Architecture

### Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
│                    (main_refactored.py)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼─────────┐
│   API Layer    │          │  Exception Layer  │
│  (Endpoints)   │◄─────────┤   (Exceptions)    │
└───────┬────────┘          └───────────────────┘
        │
        │ Uses
        │
┌───────▼────────────────────────────────────────┐
│           Service Layer                        │
│                                                │
│  ┌──────────────────┐  ┌──────────────────┐  │
│  │  F1DataService   │  │ SessionManager   │  │
│  │                  │  │                  │  │
│  │ - get_seasons()  │  │ - get_session()  │  │
│  │ - get_events()   │  │ - cache mgmt     │  │
│  │ - get_drivers()  │  │ - load control   │  │
│  │ - compare_telem()│  │                  │  │
│  └─────────┬────────┘  └────────┬─────────┘  │
│            │                    │             │
│            └────────┬───────────┘             │
└─────────────────────┼─────────────────────────┘
                      │
                      │ Uses
                      │
        ┌─────────────▼─────────────┐
        │       FastF1 Library      │
        │   (Data Source)           │
        └───────────────────────────┘
```

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Application                       │
│                        (App.tsx)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼─────────┐
│   Pages Layer  │          │  Components Layer │
│  (Dashboard)   │◄─────────┤ (TelemetryChart)  │
└───────┬────────┘          └─────────┬─────────┘
        │                             │
        │ Uses                        │ Uses
        │                             │
┌───────▼─────────────────────────────▼─────────┐
│              Hooks Layer                      │
│                                                │
│  ┌──────────────────┐  ┌──────────────────┐  │
│  │   useSeasons()   │  │ useTelemetry     │  │
│  │   useEvents()    │  │ Comparison()     │  │
│  │   useDrivers()   │  │                  │  │
│  └─────────┬────────┘  └────────┬─────────┘  │
│            │                    │             │
│            └────────┬───────────┘             │
└─────────────────────┼─────────────────────────┘
                      │
                      │ Uses
                      │
        ┌─────────────▼─────────────┐
        │    API Service Layer      │
        │    (apiService.ts)        │
        └─────────────┬─────────────┘
                      │
                      │ HTTP Requests
                      │
        ┌─────────────▼─────────────┐
        │      Backend API          │
        │   (FastAPI Endpoints)     │
        └───────────────────────────┘
```

## 🔄 Data Flow

### Telemetry Comparison Flow

```
1. User Action
   │
   ├─► SelectionPanel (Select drivers)
   │
   ├─► Dashboard (handleCompare)
   │
   ├─► useTelemetryComparison() hook
   │   │
   │   ├─► f1Api.compareTelemetry()
   │   │
   │   ├─► HTTP GET /api/v1/telemetry/compare
   │   │
   │   ├─► Backend: compare_telemetry endpoint
   │   │
   │   ├─► F1DataService.compare_telemetry()
   │   │   │
   │   │   ├─► SessionManager.get_session() [with cache]
   │   │   │
   │   │   ├─► FastF1.get_session()
   │   │   │
   │   │   ├─► Process telemetry data
   │   │   │
   │   │   └─► Return ComparisonTelemetry
   │   │
   │   └─► Hook updates state
   │
   └─► TelemetryChart renders data
```

## 📦 Module Relationships

### Backend Dependencies

```
main_refactored.py
    ↓
v1_endpoints_refactored.py
    ↓
F1DataService ←─────┐
    ↓               │
SessionManager ─────┘
    ↓
FastF1 Library
```

### Frontend Dependencies

```
App.tsx
    ↓
DashboardRefactored.tsx
    ↓
useF1Data.ts hooks ←───┐
    ↓                  │
apiService.ts          │
    ↓                  │
Backend API            │
                       │
TelemetryChartRefactored.tsx
    ↓
chartUtils.ts ─────────┘
```

## 🎯 Separation of Concerns

### Backend Layers

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **API (Endpoints)** | HTTP routing, request/response | `@router.get("/seasons")` |
| **Service** | Business logic, data processing | `f1_service.get_seasons()` |
| **Manager** | Resource management, caching | `session_manager.get_session()` |
| **Data Source** | External data access | `fastf1.get_session()` |

### Frontend Layers

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **Pages** | Page-level UI, routing | `<Dashboard />` |
| **Components** | Reusable UI elements | `<TelemetryChart />` |
| **Hooks** | State management, data fetching | `useSeasons()` |
| **Services** | API communication | `f1Api.getSeasons()` |
| **Utils** | Pure functions, helpers | `buildSpeedChartData()` |

## 🔐 Benefits of This Architecture

### 1. Testability

```
Backend:
✅ Test service layer independently
✅ Test endpoints with mocked services
✅ Test session manager in isolation

Frontend:
✅ Test hooks independently
✅ Test components with mocked hooks
✅ Test utilities as pure functions
```

### 2. Maintainability

```
✅ Clear boundaries between layers
✅ Single Responsibility Principle
✅ Easy to locate and fix bugs
✅ Changes isolated to specific layers
```

### 3. Scalability

```
✅ Easy to add new endpoints
✅ Easy to add new hooks
✅ Reusable business logic
✅ Consistent patterns
```

### 4. Developer Experience

```
✅ Clear mental model
✅ Predictable patterns
✅ Self-documenting structure
✅ Easy onboarding
```

## 📊 Code Metrics

### Before Refactoring

```
Backend:
- v1_endpoints.py: 1000+ lines
- Mixed concerns: routing + business logic + data access
- Hard to test
- Duplicated code

Frontend:
- Dashboard.tsx: 400+ lines
- Mixed concerns: UI + state + data fetching
- Hard to reuse logic
- Repeated patterns
```

### After Refactoring

```
Backend:
- v1_endpoints_refactored.py: ~200 lines (thin layer)
- F1DataService: ~600 lines (business logic)
- SessionManager: ~150 lines (caching)
- Clear separation, easy to test

Frontend:
- DashboardRefactored.tsx: ~200 lines (UI only)
- useF1Data.ts: ~400 lines (8 reusable hooks)
- chartUtils.ts: ~200 lines (reusable config)
- Clear separation, easy to reuse
```

## 🎓 Design Patterns Used

### Backend

1. **Service Layer Pattern**: Business logic separation
2. **Singleton Pattern**: Global service instances
3. **Facade Pattern**: Service layer simplifies FastF1 complexity
4. **Strategy Pattern**: Configurable session loading
5. **Template Method**: Consistent error handling

### Frontend

1. **Custom Hooks Pattern**: Reusable stateful logic
2. **Builder Pattern**: Chart data builders
3. **Facade Pattern**: Hooks simplify API calls
4. **Observer Pattern**: React state updates
5. **Composition Pattern**: Component structure

---

This architecture provides:
- ✅ **Maintainability**: Easy to understand and modify
- ✅ **Testability**: All layers independently testable
- ✅ **Scalability**: Easy to add features
- ✅ **Reusability**: DRY principle throughout
- ✅ **Clarity**: Clear separation of concerns
