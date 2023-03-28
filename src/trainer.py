import tensorflow as tf
import numpy as np

# make a label for the model to consume
# data set should include the following:
#   - weapon type hash
#   - weapon element hash
#   - weapon rpm
#   - perk hash
#   - all available perks
#   - subclass hash (optional)





class GodrollModel(tf.keras.Model):
    def __init__(self) -> None:
        super().__init__()

        #prepare the model to take in the data
        self.weapon_type_hash = tf.keras.layers.Input(shape=(1,), name="weapon_type_hash", dtype="int64")
        self.weapon_element_hash = tf.keras.layers.Input(shape=(1,), name="weapon_element_hash", dtype="int64")
        self.weapon_rpm = tf.keras.layers.Input(shape=(1,), name="weapon_rpm", dtype="int64")
        self.perk_hash = tf.keras.layers.Input(shape=(1,), name="perk_hash", dtype="int64")
        self.other_perk_hash = tf.keras.layers.Input(shape=(1,), name="other_perk_hash", dtype="int64")
        self.all_available_perks = tf.keras.layers.Input(shape=(12,), name="all_available_perks", dtype="int64")
        self.subclass_hash = tf.keras.layers.Input(shape=(1,), name="subclass_hash", dtype="int64")

        #increase weight of cerain fields
        self.perk_hash = tf.keras.layers.Lambda(lambda x: x * 5)(self.perk_hash)
        self.weapon_type_hash = tf.keras.layers.Lambda(lambda x: x * 3)(self.weapon_type_hash)
        self.all_available_perks = tf.keras.layers.Lambda(lambda x: x * 0.5)(self.all_available_perks)


        # make the model
        self.concat = tf.keras.layers.Concatenate()
        self.flatten = tf.keras.layers.Flatten()

        self.dense0 = tf.keras.layers.Dense(64, activation="relu")
        self.dense1 = tf.keras.layers.Dense(64, activation="relu")
        self.dense2 = tf.keras.layers.Dense(64, activation="relu")

        self._output = tf.keras.layers.Dense(1, activation="sigmoid", kernel_initializer=tf.keras.initializers.RandomNormal(mean=0.5, stddev=0.1))

    def __call__(self):
        # make the model
        x = self.concat([self.weapon_type_hash, self.weapon_element_hash, self.weapon_rpm, self.perk_hash, self.other_perk_hash, self.all_available_perks, self.subclass_hash])
        x = self.flatten(x)
        x = self.dense0(x)
        x = self.dense1(x)
        x = self.dense2(x)
        x = self._output(x)
        return x

    def train(self, inputs: list[dict], labels: list[int], epochs: int = 10, batch_size: int = 32):
        # train the model
        self.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        self.fit(inputs, labels, epochs=epochs, batch_size=batch_size)

    def predict(self, inputs: dict):
        # make a prediction
        return self.predict(inputs)

    def save(self, path: str):
        # save the model
        self.save(path)

    def load(self, path: str):
        # load the model
        self.load(path)