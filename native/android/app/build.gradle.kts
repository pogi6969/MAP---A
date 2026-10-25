plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

/* Google's published test IDs. Set ADMOB_APP_ID and ADMOB_BANNER_ID (environment or
   -P properties) to the IDs from your AdMob account for the real build. */
fun setting(name: String, fallback: String): String =
    (project.findProperty(name) as String?) ?: System.getenv(name) ?: fallback
val admobAppId = setting("ADMOB_APP_ID", "ca-app-pub-3940256099942544~3347511713")
val admobBannerId = setting("ADMOB_BANNER_ID", "ca-app-pub-3940256099942544/9214589741")
val keystorePath: String? = System.getenv("MAPA_KEYSTORE")

/* The app is the same single file the website serves: app/index.html. */
val webAssets = layout.buildDirectory.dir("generated/webapp")
val copyWebApp by tasks.registering(Copy::class) {
    from(rootProject.file("../../app/index.html"))
    into(webAssets)
}

android {
    namespace = "ph.mapa.albay"
    compileSdk = 36

    defaultConfig {
        applicationId = "ph.mapa.albay"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "49"
        manifestPlaceholders["admobAppId"] = admobAppId
        buildConfigField("String", "ADMOB_BANNER_ID", "\"$admobBannerId\"")
    }

    signingConfigs {
        if (keystorePath != null) {
            create("upload") {
                storeFile = file(keystorePath)
                storePassword = System.getenv("MAPA_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("MAPA_KEY_ALIAS")
                keyPassword = System.getenv("MAPA_KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            if (keystorePath != null) signingConfig = signingConfigs.getByName("upload")
        }
    }

    buildFeatures { buildConfig = true }

    sourceSets["main"].assets.srcDir(webAssets)

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

tasks.named("preBuild") { dependsOn(copyWebApp) }

dependencies {
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.appcompat:appcompat:1.7.1")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.webkit:webkit:1.14.0")
    implementation("com.google.android.gms:play-services-ads:24.4.0")
    implementation("com.google.android.ump:user-messaging-platform:3.2.0")
}
