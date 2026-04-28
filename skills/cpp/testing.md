# C++ Testing

## Framework: Google Test + Google Mock

```bash
# vcpkg
vcpkg install gtest

# CMake
find_package(GTest REQUIRED)
target_link_libraries(your_target GTest::gtest GTest::gmock)
```

## Unit Test

```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>

class MockUserService : public UserService {
public:
    MOCK_METHOD(std::string, getUserById, (int id), (override));
};

TEST(UserServiceTest, GetUserById_WhenValid_ReturnsUser) {
    // Arrange
    auto mock = std::make_unique<MockUserService>();
    EXPECT_CALL(*mock, getUserById(1)).WillOnce(::testing::Return("John"));

    UserServiceImpl service(std::move(mock));

    // Act
    auto result = service.getUserById(1);

    // Assert
    EXPECT_EQ(result, "John");
}
```

## Integration Test with Fixtures

```cpp
class FileTest : public ::testing::Test {
protected:
    std::string testDir;
    void SetUp() override {
        testDir = "/tmp/test_" + std::to_string(time(nullptr));
        std::filesystem::create_directory(testDir);
    }
    void TearDown() override {
        std::filesystem::remove_all(testDir);
    }
};

TEST_F(FileTest, SaveAndLoad_Persists) { ... }
```

## CTest Timeouts

```cmake
set(CTEST_TEST_TIMEOUT 60)
set_tests_properties(UnitTest1 PROPERTIES TIMEOUT 60)
set_tests_properties(IntegrationTest1 PROPERTIES TIMEOUT 300)
set_tests_properties(E2ETest1 PROPERTIES TIMEOUT 600)
```

## Best Practices

1. AAA pattern (Arrange, Act, Assert)
2. One assertion per test when possible
3. Mock external dependencies
4. Use fixtures for shared setup
5. Separate unit/integration tests
6. Typed tests for templates

## Timeouts

| Type | Timeout |
|------|---------|
| Unit | 1 min |
| Integration | 5 min |
| E2E | 10 min |

## Test Length

- Max 10 LOC per unit test
- Up to 20 LOC with explanatory comment
