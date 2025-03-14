// swift-tools-version:5.8
import PackageDescription

let package:Package = .init(name: "swift-png",
    platforms: [.macOS(.v10_15), .iOS(.v13), .tvOS(.v13), .watchOS(.v6)],
    products: [
        .library(name: "LZ77", targets: ["LZ77"]),
        .library(name: "PNG", targets: ["PNG"]),

        .executable(name: "compression-benchmark", targets: ["PNGCompressionBenchmarks"]),
        .executable(name: "decompression-benchmark", targets: ["PNGDecompressionBenchmarks"]),
    ],
    dependencies: [
        .package(url: "https://github.com/tayloraswift/swift-hash", .upToNextMinor(
            from: "0.7.1")),
    ],
    targets: [
        .target(name: "LZ77",
            dependencies: [
                .product(name: "CRC", package: "swift-hash"),
            ]),

        .target(name: "PNG",
            dependencies: [
                .target(name: "LZ77"),
            ]),

        .target(name: "PNGInspection",
            dependencies: [
                .target(name: "PNG"),
            ]),

        .testTarget(name: "LZ77Tests",
            dependencies: [
                .target(name: "LZ77"),
            ],
            path: "Sources/LZ77Tests",
            swiftSettings: [
                .define("DEBUG", .when(configuration: .debug))
            ]),

        .testTarget(name: "PNGTests",
            dependencies: [
                .target(name: "PNG"),
            ],
            path: "Sources/PNGTests",
            swiftSettings: [
                .define("DEBUG", .when(configuration: .debug))
            ]),

        .testTarget(name: "PNGIntegrationTests",
            dependencies: [
                .target(name: "PNG"),
            ],
            path: "Sources/PNGIntegrationTests",
            exclude: [
                "PngSuite.LICENSE",
                "PngSuite.README",
                "Inputs/",
                "Outputs/",
                "RGBA/",
            ]),

        .testTarget(name: "PNGCompressionTests",
            dependencies: [
                .target(name: "PNG"),
            ],
            path: "Sources/PNGCompressionTests"),

        .executableTarget(name: "PNGCompressionBenchmarks",
            dependencies: [
                .target(name: "PNG"),
            ],
            path: "Benchmarks/Compression/Swift"),

        .executableTarget(name: "PNGDecompressionBenchmarks",
            dependencies: [
                .target(name: "PNG"),
            ],
            path: "Benchmarks/Decompression/Swift"),
    ],
    swiftLanguageVersions: [.v5]
)

for target:PackageDescription.Target in package.targets
{
    {
        var settings:[PackageDescription.SwiftSetting] = $0 ?? []

        settings.append(.enableUpcomingFeature("BareSlashRegexLiterals"))
        settings.append(.enableUpcomingFeature("ConciseMagicFile"))
        settings.append(.enableUpcomingFeature("ExistentialAny"))

        //  settings.append(.unsafeFlags(["-parse-as-library"], .when(platforms: [.windows])))

        $0 = settings
    } (&target.swiftSettings)
}
