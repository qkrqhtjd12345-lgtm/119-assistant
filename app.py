import streamlit as st
from datetime import datetime
import hashlib

st.set_page_config(
    page_title="충남119 복무AI",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 로고 (Base64 임베드 - 배포 환경에서도 항상 표시됨)
# ============================================================
LOGO_B64 = "iVBORw0KGgoAAAANSUhEUgAAAQEAAABOCAYAAAAglaPwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAESwSURBVHhe7Z1neFzVtbDfM71pNNKMeu+WJVtyrxgbY2MMNiUmAUwcEkgC3BACIclNbpILSW7KTScJhBKqCS30ZnDBRe5dttV7l0bSaHo953w/RhaWbNNi57uBeZ9n/5g5e+/T1157rbXXEWRZlokRI8ZnFsHj8cSEQIwYn2GErq6umBCIEeMzjBCJRGJCIEaMzzBCzCYQI8ZnG8XEP2LEiPHZIiYEYsT4jBMTAjFifMaJCYEYMT7jxIRAjBifcWJCIEaMzzgxIRAjxmecmBCIEeMzzjkNFopEIgwNDaFWqzGbzahUqolV/s8giiIej4dwOIxCoUCj0aDX61EqlROrxojxqeacCQFZlunq6uKXv/wlxcXFzJw5k4KCAmw22/9JYdDa2sqrL7+Et7sbk05LUlYWWZMmk1dYSGZm5sTqMWJ8ajlnQkCSJI4fP87tt9/OFatX09DYSEFBAXPnzqW0tBSr1YogCBObfWJkWR4rJxEQEBTCR9rPtm3beOAPv0NXfZisgBcpItIgKMlddSVrbv4aWq2WvLw84uPjJzaNEeNThfKee+65Z+KfnwRBEFAqlXR1dVE6aRLXXncdtbW1bNmyheHhYfR6PfHx8f+UViBJMpIsI0sSkYiIx+PF6XTicrkJhUKIokQ4IiJJEiB/oGqfnp5OSkYmbcEQSo+TOX4P16tk6uvq2NDUTFNXN0NDQ6SlpWEymSY2jxHjU8M50wQAwuEwO3fu5IUXXuDOO+9EqVRy+PBhqqqq0Gg0LF26lDlz5mA2myc2PSuyLBOOiIRDYSRZYmTEQVtbG50dnQwNDeH1ehFFEa1WS1ycmeTkVHJzckhKsqE36DAaDOj0uondjuF2u3nppZd479GHuL6ljsnItF94Eeav3MJTG94lPT2ddevWkZiYOLFpjBifCs6ZJgCgVCoxmUx0d3fT2NjI/PnzsVgs2Gw2XC4Xhw8fxuv1kpGRgV6vn9j8NMKRCA6nB/ugg47OTnbv3smWzZvYt3cfNTU1dHf3Yrfb6e3tpbGxidqaGlpammlsaKC/r49QMKodiKKIWq0+oxai1WqpqKjg3X0H0DTVkSbIZHZ3YbNZKbt8NdsOHGRwcJCysrIP1CxixPh35ZwKAQCdTofBYKCqqgq1Ws306dMxm82kpqai0Wg4ePAgdrudnJwcDAbDxOYwal9wujz09Nppae1k9+49bN2yiYb6OvR6A5WVM5gx4wJycsqwJeWTlJRHdnYxBQUF6HRqenq7qa+vo7m1BYdjmFAoTCAQRBCixzfxZXY4HDz9wJ+5csROrUZFfiBIpK4Gk9FA8oKFbN61G7PZTE5Ozrh2MWJ8GjjnQkAQBOLj4xFFkaqqKpKSkigoKMBsNpOZkYHFPcL+V1+i0zGCzmhCoVAgCAKiKBEIBHA63fT3D9LW3s3hI0fZvOldGuqOk56WwtKly8nPn0ZbZ4Td+zrZva+dw9W91DUO0dbhwj4UQaWOp6SkiLQ0G/aBAerr62lrbcXlcuN2uXA5XYTCIZABAcLhCD09PTz/5JNcHHDTIygQBUgKBpBamrEk2RALitixZy8FBQUkJCRMPOUYMf6tOac2gVOx2+08/vjjSJLEXXfdhVqtJri3Cs/TT1Dz3hZeQYV/1gIKy8qxJCRgMsWh1xtRKtV0dHZSXV1Nb283qSnJLFiwgNy8yRw9bqdqZwNNLXaQBRIsBuLidOh1ao7XdGM26xh2eMhIM1BUYKEo34jD0UVjYwPDw0PotDpycnJIT08jPt6CTq9HoVAQDoZ45dWXMe7dzlKdihyVQL4oYRQllJmZuK+5jldlNd5AkM9//vMUFRV9JA9EjBj/Dpw3IdDR0cH69etJS0tj3bp10NeF5/e/IvDqK4h+H8+h4DGFEVtBIQqFEp3eiCAIBINBtDodqalpFBeVUFRchtujoWp3C4eOdOD1Bli2pAylQiAlKQ5bkhmFQuDAwVYqK7LZur2OXftbMBnVFOZZmDY1mcwMLb29HbS1tdDW2opjeAi1RoPBaEKtUmFNtNLZ1Ul2TxNqj4clGiUXCqAVJVAqUZaXM3TtOja7A3R0dJCRkUFubi5Go5GKigpsNtvE048R49+Gcz4dYHROv3//fmpqavjiDTegb2vC++Cf6N28Ccnl4l1JphcBImEO99kxmuMwmUxYrYlMmlTK9OkzmVY5G40mjR27u9mwsYbqE924PQFA4OLFk/EFQhj0apSCgCjJ6HRqMtMTOV7TTVfPCKGQxOBQgJ4+L4GQkkklxcydM52KinIKCwuxJCRiNBpxOV0cO17NHEWQm1MtpDkcPOSLMFetxCLLIMvgdBJv0FN05VXEpaUTCAQYHBzk7bffJjMzk5ycnJhmEOPflvMiBDweD4cPH0ahULCkKB/vEw/R9ObrPNQ/zLaITK0ssyzRwlIpjD0cpDYQYfHiJcyYMZPsnFL6BpTs3NvLezuaOHaih8FhL5IUVVgkSSYYitDcaqe2oY8TdT2cqOuhqcWO3x/iyPEu/IFwtK4s4/GG6e3z0NLmwD4YwpqYwsyZU5k6pRy93kBV1VZmSF5uSrGQ2zfANn+Q/dZM/B4nCxSjL3YkgjziwJydQ+Hqq8gvKMBgMHDs2DHKy8vJy8s79fRjxPi34rwsIAqHw4RCIaxWK2JDLU27qnjKF2F4ziJUl62hNTGddoOejJwMvm3UsCDkYsM7G6LRf4KCnXva2LW3lbaO4bEX+iQKBXT32NGoRdJT9OTnxFOUn0h+XgIujy+qHSjHj8qBQIS2DgfbqprYva+VYEjG5/fy+msvMSXk5KtpVrJ7+nh62MnbSdnc/M272a8xEVa970WQ7HaC27cgd7QQb7FQX19PXl4e+fn54/YVI8a/G+dFExBFkaamJgYGBpipU3Pwnbc5kZJB5YrLycovYn/1Eao6erBZ4phhS2Ca00mj28mmplYWLJhHZnoyTS3DuD1BAAQBzEaZghwlC+cksXxJEcsuKmfxBaUsmF/InFn5zJ6Zx4zpOSxeVMy8ObloNQJ+fwiPJ8RJo0dRQRLXXDWdeLPEA/ffh6nhKDda48jp7ePpoRHWo6fDF+CLN36VI4f2M90zhGVUA0GhQJWfj/aCCznR1cumTZuYO3cuFRUVKBTnRZbGiPEv4bw8vQaDAavVSldXF4PhMEJiIgajkcTERAwGA2q1lqtu/BqPO0K8JUqkFOXxA4VEYVcT9933WzLTtay7fiaZaWZMBpGKUpnPX5nJN25dxjVrLqSgMInaun309DRisxrZt28rr77yDAP9rXjcPSQlwk03LuTb37yQz19VTHqKnoI8K19YM530NBUPPfgXNMcP8iVbHDl9/TwzNMI/tPGsvf0uAgE/giBgSbQyrIhqAoLJiP7qq4n77g/pVep44YUXyMnJYf78+WcMQPo4yDIEgxH8/hD+QHjcWoiPgihKBIMRQqHIx24bIwbnSxMQBAG9Xk9jYyP1DQ2EdTrsKi1FlTPwer00NNRx9dVrmD53Ib9+9U1sZg3TkpOoHBrkuGOYLa3tXHzRQlJsIhmpEa66YiF5uekkJMRTW1vDjqrtLFm8mPLyKSiVSjZt2sz1a9fy97+vZ//+fcSZjEwuLQGCVEzNIy0F8nP1pKcbWb/+McRDO7k5xUJ+bz/PDTp4QWfh5u/fQ/mUCp548jGu+fxa9u/bxeIFs8lefCHGb9yF4fqv0BmM8NeHH8JgMLJu3ToSEhL+aYOgLMv87r4N/Oiel/jbUzuYVpFNakr8R+73uRf28b0fPc/j66sozE8mKzNxXFtZhtfePMLLrx6gtX2Q0pJ0lEoFsiwTiUTXYERnYR+88Oq5f+zj9TcP09E5RNnkTBSjdWUZIhGRUFgc7e/DiyzJKJUff/yJiBLhcARRlFF8yPEGgxG83gB+fwiVSjluf253AJ8vSCgUQatV0dM7wkOPbuPg4VY0ahVpqZZxffX0jrBxywn27m9FrVZis8adtu9IRKS+sZ83366mtX0Qg16NJX58MFx7xxAbN51g/8E2tFr1aD/jqhAMRTh+vIsNG4/T0TmE0ajDbP7w6Np/hvMiBADi4uKwWCy8u3svNUcOk5GWijE9m77ePhyOYRYvXsLUqVMpq6zke0/8nWyrkUqbjYqhIWrdTg4PDVJYkEVWdhrHTxyjoakRvc6AJEtEwhFqamuoq6ulqKiY9o42tm59j7KycoaGhpg7dx6hcJhf/eoXyLLEzFnTEQjz0j+eQ9NQzU1WEwX9dp63D/O8zsKtP/45ldNnYTSa+MeLzzFn7kIOHD7AbX/4E/EXr8RvS+HNTZv43e9/T2FhEbfccguJieNfto+CJEkcPNTOo0/uYHtVA9urGtixs4Ej1R20tQ8xMuKnq9vBiZoeqnY1sr2qgZ27m/AHwhTkJ8Oo0HC7A/T2ORlx+mhts7P/YBsdHUNYE03YrHH4fCFGnD7MZj2CAA89uo1nn99LW8cQixYUkZhowh8I8/hTVdx066Ns2lJDdqaV7CzrxEMe4w/3vcvLrx2io2uYz105A40mqgFJksSTf9/FTbc+yv0PbuHBR7Z+YPnb4zuore/jshVTJ+7iQzl2oovlq37D409V4Q+EmTenYGKVMfbsb+Y7P3iBX/3uLdRqJaUlaWPHfNsdT/Hf//MKGzYe5+orZtDROcxPf/E6Bw61kZBgYN6cwnF9+QMh/udXb/Diywfo73ex7OJy1KfYiwACwQibt9Tws1++TnOrncKCFAoLovfsJC5XgHt//iqvvXEYp8vPJcvKT3uGvJ4Ar715mN/8YQMdncNMKk4lN+f8uqD/OV32AxAEgalTp/Ltu+9m/fr15ObmkpqSzo4dVeTk5JBkS2TXrhYWLZrNo089zXWfvwahMo+F5aXMMKdivGQFidZE9u3fz9GjR0lMTKSv7y0KC4tYevHFZKRn4HQ66e3rZcaMmVy6IgWLxcKyi5cjAy+++A/S09MpLCrmmb+vp6CgkCuvuJKhTWoMe3fw4sAQz+sT+PqPf05l5Uz27W9n/vwCpk+fSfXRQzQ1NvCje+6lp6eH1tZWKisr+c53vsOsWbNOu3EfFVGSqanv5m9P7Bj3/6lq/K49Teze2xQNZwQ0GiXhiMjypWUA+ANhnv3HPn7+v2+MtTnJw49t5+HHto/9PnHwZxgMGkRJIiKOjsKjuzLoNSQnxaNUKGlo6KO72xHVCM5yapIkExElRFGKDv+jKJUKUpPNJMQb6OgcRhCEs/YBIInRBWGfhNKSNPx+Eb8/TFVVPXfevnxilTGyMhIxGjQEAmEOH23nc1fOxGiMLiQLhSIEAmGCoajRWZZlRFEiIoqIJ21Ap5Bki0OtVhOOSFTtbeA/7nzqNE1GFCV6ukcIR8SodnWGftLT4lEpo/eztrEPUZJOm5FLUvRYwhGRiPj+/TqfnDchcJLCwkLuueceWlra2Lt3P02N9Vy/di1ut8j9j2znSHUnt3xtEY89uZ47bvs6N150IZkXLMVoNOEcceL1eikuLiY9LZ2FCy+gubmJvz5wP8dPnMBg0GOz2RAUCgbtdgYHB5kypYJLLlnB0qXLaGtvpa21hcppMzAY9MgCpK+8imeGHBySddxy13eYNXMu9z+4g70H25i/oJArrriCvz36KPf+9FcY9SpKSorIz88/J8uJlQoF06bmcPcdl8CoCzMQCLPh3WO0tNmRZUhPtXD5ygri4nQoBAGlUkHZ5PeTnAiAXqcmyRYHoyOQzxdEFCW0WhVGoxalQoEky6MPlHzWB0mvV2M0aenr8xMIRu0RHybgZFkmEAyPqdhqtRKNRo1Go8Zs1nPvD68cHeEmtnwf5Sc0pGo0KsxGDU6PH8/oOU98GU+i1apQqaLb6hp6eezJHcSZokKgo3NoQu1RZAiHIni9QRQKAY1GNda/Wg0KAfy+CDt3NZ12frIcFQQfhEqlHGvXUN9LUfl/Tqzy/4XzLgQAvF4v9fVN7Nm9l7g4M0lJaWzf1YLLHeD5Vw4TCkdYe90M7vj2d9Gq1SiVSmrrahl2DFM6qZSsrGxGnA5+9/vfYI4zcd2a1cz77S/RmK10OwLoNQpSLQbESIQdO3bwwgsv8Pzzz3LN568jJzePzZveQa834PV6KC0tpXL1VUwRRcrLKnj0yT1s3t6Azx/iyJFOLr30Un71v7/E6/MxqbiSyZMn/9PGv1MpLEwhKyuRSERiwO7ixVcO4nD6UatVyLJMb/8ITpefK1dPJyXZHH3RTlE99XoNX7x+PjdcNw+ANzdU87v73qGl1c7ll1Zy97cuITUlnvaOIQ4ebkUSZewDrlOO4HRkebw28kH0D7j4/o9fxKDXMH9eIV/43OyxbW63H7fbj0qpGFO9zyWRiEQwHB29RQnCYfGsQuBUurtHePypnWMvYDAUmVgFgEAgzDPP7eHtDUcpLEzltq8vZeb03NGt0cZxRh3f/+5l6HTqcW1DoQh79zfz0quHxv1/NpQKBVbr6QOLLMv4/CG83qhn7F/Bh1/BfxJJkmhoaKK+ro4TJ6opLilBELRs3d6AZ/REX3nzGI8/8S7BQIDUtDRef/MNfH4fa6+/gdS0NA4fPsSWzZu55ZZbuO9n/8UFnEC14y9s2nmQW5/YxVcermLY5UUlulgyt4w//eF/+elPf8LOqq3s37eH6667nqysTJzOEbxeL2kZGSjVah58ZCMbNp3A5w8B8OwLB3C7g1x/3Q28+tILDA4N09nZ85FfkA/D6fLz0isH+OZdT3PtuvtZc/1feOrvuxCASy+ZwtIlk0lNsfDya4dYdfUfuG7dA9x+19P86YFNZxjNBZwuP4cOt9PdPQLA3gPNtLYNIooyb26o5tY71vO1259k7/6WiY0/MYFAmIOH2zhwqI32jvEjqiyDzxf6xOr+h3GitptAMGrI9HgCNDT1TaxyRlJSzKy5aibrbljAuhsWkJF6lmxRgoAsCIiygCRHNYOTaNQqBIWALMiUlqQxrSJ7XJk6JYvMjI+ecyIpyczGN+5my9vfGVdeef521q2dP7H6eeW8C4HBwSFqa2s5ePAASpWS/PxCDh/to6tnZCwKUKmU8bg7KCsr42h1NfPnzUMhKFCpVVQfPYLX6+F7d32H2WUzidTvJbDnWfwbfoOnpxFJlhAUMqHu7YT2/5DQvv9Gqn2VyhQVP/2v76LXa3n55ZcoKChg9erVqFQqNm/ejNlsJiFBAUQFAMDx2l7e3XScRYuWMDho59ChA7S3d+L1+k45o09OMBimvWOIhuZ+wmGJnBwbS5dM5of/uYqf/PBK/vTbtfzo+6u45OJySorTCIZEmpoHqKnpGXsiZVnG7w/R2TXEc//YxzubjiPJEhqNiu7uER58ZCsHDrViMmmZP6eQRQtKSE46cxIXQYjabgC8vhAulx+PJzCuuNx+7INu/IHodbJaTXz3zpV879srWXFx+YQeo1OcU1+ec4EM2AfdPPjI1uiUBRhx+nj6mT0MDrnPICBP2jai55aZlsgtX13C9+5ayffuWklu7niD3Uk0GhUrV1Tw8F9u5MffX03ppDQYtW9Nm5aDJd6AxxPg2nUPsPqa+8aVz99wPw/+bdvELk9DrVYhCALhiIh9yM2wwzeujIz48PvHB8idb86bd4DRyMHq6mq2bt3O8RPHKC2dTHJKAdt399Db7xkTAinWINdcOQ2ny0ldXR1KlYqSkhLq62oZGh7i1q/dgrpfpvmNY/idEdQKLwghVBUrafQbuaYyhdLaG5B7NiNopuJ96U+EDr5IfFYJpRetobm5me7ubvR6PS0tzRQVFVJeXo7RINDUbGd4JDz2ILW1DzO9IhWLxcjGjRsoLi5FoVCQkpKM4mQY8ScgGAzT1+ckHJHIzbGxeNEkrlw1naWLS0lLteD3h3G5/NisccybU8Dc2fkUFqSQm2MjL89GcpI5alQKR6ja1cD9D23h5VcP4fOFmD4tl7LSdAKBMCdqe9izvxlbYhy337aUdWvnc7y2m/qGPizxBlZfVok1MaqG9vW72H+gFfugG1mWGRr2UtfQy7ET3WPl0JF2Nm46zp59LQQCYVJT4vnvH6xmSnkmKSnREbWjc4jde5sYHPKQk20jyRaHxxNgaNhzenF4CQTCmOM+2O0lyzLBYIQRp5+WNjt/e3wHr7x+CJ1WxaTiNBwjUc+IzxvCaosuSVcqFSiVUddhJCKxdXsdrW12ADLTExgc9tDeOcSWbTUM2N3Ex+tZe+08hoY9vPL6YWRkFs4v4orLp5GQYBw3pcnLTcLl9qMQBOLjDcSb9fT2OfH7QygVCvJybFgTjSQnmcnLTWL2zLwzeltqa3uob+rD7Q5w5EgH23bWs+m9mrGyZVst1cc6cbkDJNniWDCviLzc8+sdOG+rCAG6u7t59dXXeeONNxAEgSVLllPXKBMMqhly+HC6AgzYncydHuLGL65i/4EDeL1egqEg0yqnsWvXTr5+y9cpTM+n6bVqunc2ExDCxE9LID7JTsiSQr3HwvLiJEzHrkchOhGsX8H7/I8QtHHoLroV45pfUldXxzPPPENiopXCwkIG7XYkWaJ0UilvvX2Yl95sw+N936hz8eJcFi9MYv36x0lLy+CylZdx4eKFJCV98pvR3DLA/Q9uYXDYO3HTRyLBYuALa2aTmZHAffdvYtOWEyQnmZlWmcMX1swmL9fGm28fZcPG47S02nGMePnNL77Apcun8K3vPsOrrx8mJ9vGI/ffSFFhCgC9fSM8+fddvPbGEVxu/xlHVI1aidGoxTHixeMJUpCfzKvP345p1MgGUN/Qx+//9C6b3qvBoFeRmZGIXq8Z189JlEoF0ypz+P7dl03cNA63O8C2HXUcPdbFtp0NNDf3k5xkZvEFxXx53QU89Nh2qnY2MOzwUlyYwvx5hcycnsfsGXlYLAYkSeaRx7fzxPqd9PWPjE7pooqvLEfvdWaGlbde+RYNjX3c+NW/ERFFbrpxEXffsWLsOMRTLPSSJNHf78TrD4Msc/2ND+IY8VFSlMoffn3dWBu1RoU1wYjJpEOhEMYNHvUNffzpgU20tNqj3oEzXPOT5Ocl8eV1FzB75vldm3LeNIFIJEJNTS0bNrxDV2cnk0sno9VnsP+gnRmVecyenke8WU9Pbzcrluaj0+uoqTlBX38/K1dexrHqakpKJzFl9kKaBtzIgTAhr5MGdxudwhCiLZX2/iGGO5oJd4QxaPNR2GZhzCki3LAf2RiPd8HV2HUiKbZ0gr4wzc0tZGZmsmfvHnp6epk9ezZGvYojxwZwud+fFgzYvRQVJJCaHE9V1XbS0zLQG/RkZ2V+qPX8bAwOutm2vR7HiJdQKBrhd7L0DzipreuhuXUASZJQKATC4fF1FEoFU8oyycxIQBQlCvKSuebqWay5aiZ5OTZ0OjVTyrIoyEtGEKKGp8LCFJJtZppb7fh8oej0Y3Ep8aNBLHEmHbnZVtLSLOTlJjG1PIuKKePL3Nn5LF1SilKlRKVUkptr49JLpqJWv2+sNMfp0GrVBENhtBo1gkIRTQp7hiIDqakWFi0oPuXqnE5H5xC//M1bbN9Zj16rpnJqFl9YM5tbv7qElJR4Zs/IxWTUEYlI2O1u9uxrwT7oZuqULJKTzAiCQE62LRq0YzGQl5dEYUEyhQXJZGclYk00kZVl48KFxfh8IXbsasCg1zBjWu6YMTAYirB3fwt797dQW9dDXX0vnd0O+vud9A+42Lq9nlA4jN6oISfLSv+Ai/4BFz29IzS3DFBb14NKpSQx0TQWXGWzmpg7p4Dysgzmzy3kgoXFZy1zZxdQkJd8VoF6rjhvmoDD4eDNN9/iySeeRKlSsXjxcqprwtTWubh0+RSmTM5kw+YTdHYc47++dzWZmRns3bcXSRTJzMzk78/8nR/8973s7PDzdnUXVxaZSXE2s7v6GB5RpLy8jM7OLoaGhkgMx1HqySC9NJspM18m0uXHJcpsq0yn19vC4px1JEXKeeaZZ0hKSiYlJZnU1FQKCgrp6erht/e9x7adbUiyTE6WlZ7eEUqLLSxfYuWtt19HrdZw9dWfY/XqlcTFRV1zHxevL0hr2yCh0PtGM1mWGRnxsWVbDW+9U43D4WP15ZWsXD6V5GTz2JyW0RE5I91CQoJx7L9T8flCVB/vYt/+5jF1U61WkZttxWTSkZ+XREZ6ApMnpWMwjH+ovN4gx2u66f8AL8KJmm6GHV6Sk8x887aL0WrHW/9FSaK3z0l/v5NIRKKtfZDWNjuhsMiMyhxs1jgYtUHEx+spKUod134i/QMuXn7tID5/iKKCFGZNzyMlJZ5jJ7rw+0Po9RomT0qjp3eEQ0faaWm2k2g1sWzpZDLSx2d/CgYjSJKEyx3g8NF26ur76Ot3ApCWFk98vIH+ficZ6QmUlWYwrSIbRu0O3//Ri2x+r2Zcfx+Hu+9cwbVrZtPUMsDIyCe3LZUUp5KeZvnEg9AHcd6EQEtLC4899jjvvfceeXn5lExayLvv9SDLahbMLWRSUSr3/20r2amD/OLn38I8+nIFAn42bdpEb18Pt3/7u/xjXxtPVDVxgdXPYpuPLoeXjp5+5s+fR/XRamQgPyuPgY2tzJ9RSmHCt5GtS2izTuWNwLsERC+LsteyKPMGnnjiCRwOB9dfvxajMfoy+Xx+nnlmN088e5AFcwopKUpl6456mlv7WPv5fPr76tn63hbWfelGLr10OcXFHzyCfVT8/hBHqjvZvrOB3XsaqWvoIxAIU1KcxrzZBVywoJhFC4vHjbhnw+8P8c7GYzz5992cqOkiMdFESnI8LpeftnY7ySnxXLtmNuvWLiDxDEKko3OI3/7xHbZX1U/cdBq5OUmsf/SrGI3aiZvG8fRze1j/zG6cLj+//cXnmTu74GM9wCcfy4ltvnn303R2OsjKTOD3v75uXMxBtMmZYx0GB908+499vPbmERqb+jHH6dCoVThdfhKtRi5eMpk1V82kYkrWWPtoDMdxmlsGJnb3kblgYTGZGQn87+/e4mh158TNHwlBgDu+sZzLLq1A9RFcoh+X8zIdkGWZjo4O3nzzDbweD8XFkxhxG6htcJCemgCjrqSGpj6mTNJy4YXzxpJ/ejxetm3byrz58ygtLiJe4UTt70Sv0SAISnQ6HYmJiWRkZKJSqTCbzQw6hnBFPJRMM2FxPEco81I2+0qRpFQIFZBhmkauLYPBwUH6+wfIzMzEYonGhysUChwOL7v3tXHpxeW43QEA6pr6sJi1pKVqqautISkpmYyMdHJyoqPEP0MwFGFbVQN/eWgz72w8jlqtZEZlLiVFqQzY3WzfWU9NXQ8mo5bJpekTm5/GvgOt3P/QFqqPdTJ9Wg5fvH4+l62YyoxpuahUCg4ebqe+oY+EBCOVU08//uERH5veq6GmrocEi4HplbkUF6WSl5s0Vnr6Rhgc8mA0arn2mtkfGgewa08T27bXYbe7ufzSSnJzbGd8Oc9GNPLw9Pp/+PM7nKjtAVlm7bXzxs23T/V2nIooSjzxVBUPPbqNvn4nK1dMZc1VM1gwr4jUVAtNzf0cre7E6w9ROil9LOZfpVIyqSSNeXMKSEkx4/OH0GpVXLJsCpdeMoV5cws+tGRmJBAKizS3DCDJkJhoGlfMZj3Ha7pwjHhRKAQmT848rU5igolZM/LIybb+U8bps3HuxcqoAcXr8TLiGEGlVhMfn4DTFcbnF0mwGOnoHMLl8qMQwGYbr+KEw2Hsg4PRPH7BQbKdr/IF1SOs1P4Dut9Bp4xgNBppa2/H5/NRUFBAf38/qSWZbDteR2P6ajos2bgDWeyrKeJwfRl76jXYXQGSkpJgdKoij329SCApyYwky9TV95KRnkBOViKiKNPT50On02GON9PX24PLeXZ1+ePQ2mbnxVcOcPBwO6Uladz2tYu4+1sruPtbK/jet1dSXpZBY1M/f3pgE20dgxObjyMSEdmxs4GGpn7izAbWrV3INVfPYsG8IlaumMqd37yE3FwbTpefN98+OhabcTby85K56cZFfPuOS8aV/Jzotft3pLNrmNfePILbE6SyIpu771jBl25YyHVfmMM3bl3K566cQcAfYu++FvbuOz2mQhAETtT28OAjW/ndfe9Q39A7JqQ+rDBqM/nCmjlj9/jUcsd/LEOtUSIIArk5ttO2nyyVU7PP25L189KrJEmEQiHCoTAKhRKDIQ5REpAkGZVKyYzKHAwGDYIgYzQYxgkBURLxeNzRvH0RH/LwMYz2d8lwvkGysg+NVktWVha5OTmUTpqEUqlk3vz5LLxgIeUzF/NGk5UjLXbSFE7k4Q7inO2I9jYcw8PodDpAJhAIII+F1UqYTFoUCoFQRGRyaTrHanuQZfAHJeJMJuLizHh9PoLBD36BPiqtrYPU1vYgyLBsaTkrL5lKUWEK+XlJLF9axhWXT0elVNDV7eDgobaJzccRDEUYsLvw+UIkJ8dRWJA8bpTOzrIyqTgNSZIZGvbgcHywd0KvU5GSbCYjPWFc0evObJxqbOrnifVVPPrk9nHlwIEWAsFoZN67m47z6JM7xm1//sV9pwUbncTrDbJh47HT+nz0ye04hqNeDMeIj8eeOn2/O3c3EpiQiKatfZARlx9Zllm0oGTM5SYIAjariYXzi9HpNDgcXjq7hse1PUkwGGbE6cMx4iN0lojDs6FWK8nOSmRScepppagwBUERPRajSXfa9knFqZQUp2KxGE4LVT5XnBchwMm5nABqlQqjwYBGHX2IAoEQGemWqHFq9NNlJxmdBaJQKJAkCUGfjGrSzWjn/x6x4iekzroJW2oOCQmJDA8PY4qLLunMzcnBZDIxf8EC4hVZpKjy0DYd4evt2/jy1idYtPtlQh0NRCLv37yxhRrhyOhcUiAcFomEJSaPBolo1GriLRaUyqikPlc3QRSl0cUjMjqdCtUpYcGCEI3pR4hekFD4g6Pv1ColBoMGlUqBw+HD7Q6MxV9AtH1n1zCCEA2GOdW1dyY+roWorr6XB/+2jQce2jqu7N7XTHD0ZXzrnWr++vD47U89s3vMhz8RjzfI628eOa3PBx7ayvCoEBt2eHnwkdO3b9tRPxbYdBKDQTM2ik40fkqShNsTICJKqNTK0wyeZ+JjXqL/85wXm4AgCPT29bFr124QoLx8Ci6PmsbmIcpLM6LBKjLUNvRSPimO8vJJCAoFyBDwB6iuPkJZWRm25DQUxgyU1gqcQjZKQwrmODOhUIim5ibS0tLx+300NTVSX1dHKBTC3jdIVihM9hv/IEf0k9DRitLjIlI+FbdGR3d3N7m5uVitNsLhCJFIhMFBD29vrGFSURr9A056+5w0t9gpK02jcmoyu3buxGa1UVExlcKi8ctMPwnBYITa+l7aOobweUOkp1tITY1HoVBw9Fgnf33kPbp7Rogzafn2t1aQYDndmHcShUKBc8THidoeBgZceH0hcrKtJCaYGBr28NDftrFxSw0qlZIVy6aw/OLyMXfVSfz+EDt3NdLUPACyHF1U1O+isbl/rGzZEZ3fJyYYue6aOWPaRiAYRqkQKClKY1LJ+2VKeRbTK3OYMS2XsskZ47ZNKkmjbHIGFVOzsZ0hfl6SpLHApIntplVE+5xWkXPatkklaUyrzKYwP2WcQdVk1FK1p5HeXie9/U5sVhO5OTZkWebAoXYeeWwbre2DFOQn87mrZpKTfXqQT3OrnR07G/D6QqiUCmRkmpoHxl2jk6W3bwStRv2hApdRIf3w49sQIzLZWVauWj19YpXzznnzDlRXV/O73/6O7u5uLl91JZKQw9PPHiA3y0p6moVEi5FX3z7K1SttfPmmNaiUKmTA5XLy7LPPMG1aBatXrx7rr621FUmSGXYMc/ToUYLBINnZ2YQ8LgpefxbBOYK5vAz3voPEmQzEaXQY1lyH+ze/wF5QTPC2O+lxeairb2DFikuxWpPGNINDhzv4yS/f5q7bLmbY4aW1Y4gNm05w85fmU1Sg4J57fsxll13OyktXMHfenFPO8pMRCIR5651q/vLXzXR2O8jKTCQny4osCPT2OmhuGUCpEviv76zi+i/M/dBFMsMOLw8/uo1nX9hLIBghN8dGYqIBny9Ma6sdtyfAgnmF/PTHV5/xAQ+GIjz4yFYefXIHHk8AmzUOjUY5zkU5YHcRGM1rcGqwUCAYxjOaBu7joFAImIzaMxoYJUnG7QkQ/hAt6EzotOrRkf/9Y5dl2LWnkR/e+xJt7UOkp1nIykxEo1LROzBCe8cgiQkmbv7yIq67Zs4ZPR+dXUN841vrOVbTjV6vwZpoHHd9TiUny8pNX17E4gtKJm46DY83yOwL7yXoF1kwv4gnH755YpXzznnRBAACgQDd3T3U1ddjNpuZOXMWjS2DKFVKFs0vIjMjgYNH2rHEq5g9e9LoSj0ZAQG3x83hw4dYunTpWH/2wUECgQDp6ekoFAqys7NJTU3F2dpE7hsvk1RcjOrIUUyiiHqoH9k+jNjTiTcQxPe5z5M8ewGHDh8mEAgyc+asMZVZoRDYtaeF/YfaaWsfwun0U1vfi0IhcNO6udTVHeXYsWoWLriAadMqsCSMzzrzSVCplGRlJlJcnIokSjQ29dPQ1Edb+yChgMiCeUV879srWXZRGVrt+NVqZ0Kv1zCpOJXMzEQcDi91dT20tQ/SP+AmNc3Ml9Yu4LavXUR21pkToaiU0bDX1BQLCRYjKclmUlPix5WCvGRKilIpn5zBwgXFY1MY1eh05OMWvV5zVuEmCMLYy/xxi0YTjc0f3x+kpVqYPj0XKRK93k3N/XR2D+P3h5g3p5DbvnYRK5aVE3eWcGaTUUdpaTp6nQaLxYjVasJ2lpKVlcjU8kzS0z78WYlEJLbtqCM+3khJUSpLl0yeWOW8c940AbfbzTsb3uXRRx/FHG/mK1/+KlV7htn0Xh0L5xWSlZ7I9p0NaDQhvnvXZSSnRF2HkizT2NjAk08+zv/8z89IS0vD6XSye/dugsEgJSUl7NmzZ8z4ON/nIHXDWxivXIX/+X8wsPgiBv0+pti7CLc04Jh1AZ6rv0ic1cZLL71MdnYOF1xwIQBKlYJwOMLPfvk2W3c0IYoSarUSWZK54rKprFtbyb333oNBb+DyVau44opVaLVnNpB9EsJhEZfLj8sdwOnyISAQZ9JiitOTYDF8pBiBU/EHwjidUbvAiNNHnEmHyaQl3hz9UtMHIcvRDDoBfzi6COgsKJUKLPH60160fwckKRqc5XL7GXb4EEWRBIsBs1lPvNnwofYAUZRwuwPRVZJnv0QoVQqMBu2H9sfoMfX1O5FleTTl2OnTo/PNedMENBoNAX+Arq4u6uvqSUiwcMHCuRw93k1SYhwzp+ciihKHjnYxf24O1sR45NGHUalUMTIyQl1dLXPnzqW5uZm+vr4xgRAOh0lOTkajECjoOIqpMBM0AqjDVE+7EH+cmTzJgTczi8ElqyidNZdt27bR1tbBxRdfEv0oqUqBQqGgp2eY5188zLDDizyaGMJs1vPfP1hFzYnDvPX2W1xxxdWUTykjK+v95B7nAqVSgcGgIcFiIDnJTEqymcREUzQxyFlGyQ9CrVJiMumwJppIS7Vgs8URb9Z/pIdREKJWbL3+9NH11KLXqf8tBQCjGoZer8FiMZCSbCY9zYLVGr3eJxOQfBAKhYBOp8Zo0GI0nr3o9VFD7UdBEATi4nSY4/QYJkRy/qs4b0JAEAQ0ajVer5f29nb6+vuYPacSndZMW9sgh6o7eG9HPYNDPgrzEikqSgMEZFlGpVajUCqp2rGd1NRUDAYDJ06coL29nYGBAQb6+7Hb7fiDQcRJ0+hOLaA/KYe2zBIO1TYQVmnxlExnJK+MzEmT6e3tY9PGTVRWTqeoqAiVWolSoUCMiGzeUsvufa34A+97Dm69+UIqK1K5997/Zvas+UyZMoVZs2ag0ZyfmySPprc6uQLuXCAI0Wv5URNv/P9GFCUkKRrtd44uwQcS3c+H70geTcj6YYlN/505b0IAQG/QE4mIOEZcVFcfRSHA8mUL2Ly1gX0H2ggEI8iA2xVg8aIi1Gp1VBUVBKyJiYiiyMuvvMy0ykqsViuhUAi3243X58PhcGAfsFPb0ERrRzd99mHcviBxZjMajQZRoSApLeoff/HFF9HpjFy+ahVqjQqlQoFCITA46OTx9fto7xgec43lZCbys3uv5Lln/86xYydYu3YdRUX5ZGRE3YbnAlmWqa3rZf2zu3ntjUOIksy9v3yV3GwbaakfPdPwh1F9vIsv3fwI69YumLjp/xzPvLCXt989RnlZdN59Jh5+bDtvv3uU3fuaGBr28vv73mXVysqJ1cbR3TPCm28fJTMjAY1axW//+A6TS9PRT8gMdDZ6ekf48c9eITvLeta8DB+VSERk2OFDq1Wdl8i/T8p5FQKCIGA0GvH7A4yMODl27BgZGRmkp6VT1zgwltHHPuiltDiFtAwLkiwR8Hmprj5Ke0cnkTAcOdpA9bEuqo/3c6JuhNpGPy1tMj39Orp7dXT3amjrFOgbUDMwqCIYjkOhMONy+mlqaiQSCaPX6/F43JjNcWi1WkKhMO9uqmHbjiY8vuhxKASB7921HGQvP/jB97np5lvJy8ujomLyOY3W2rOvmT//dRNxJh1z5xSSkhzP1h0NlJVmEAqKmIw6JEmmf8BJnEnHyIiPYDBCMBRheNiLfdCNJMlodSoGBz3YBz24vQEUQnTZamfXMH39ToLBMK+/dZRLl09hYNBFvFlPOByhu2eEkREfBqMGWYb+ASf9/S5Uo1OkwSEPLpefnt6om1KhUNDd42DA7kKUZMRINLHJ8HB03wqFApVKSV+/k+7ekVFVWGbY4WVo2MOI04dCEGhsHiDebBhTlWVZxun00d0zwtHjHfj8IWZOy8PjDdLd40CpVKDRvm/o++FPXiInK4npFdlMnpRBeVkGZrOegQEXvtHvNvT1OQkGI+h1UQ9BU/MATz2zi7mzCzDotXzjzvWsuWomOr2G1lY7Xm8Ik0lLMBims2sYp9OPXq9BkiQ6u4bpH3Cxd38Ls2fmodOpaWmxgwBuTxCVUoF90INBr8Hp9BGJSITCETo6hvD5Quh1apwuPyNOPyNOH0+s38mm92qYVJyGVqOioamfQCCM0aDB4wngcPii01KgvXOISETEYNCes0HhbJw3w+Cp1NbWs23bDl5++UWKiydx+eVr+OujB6g+3oMoSqhUCq5eNZmF81Oor2tAq9Wj1iTT3umnrX2IoWEf/QMuwuEIFVOy6O130d45xJ23LuWtjcdpbBlAkmS+dctSHnp8O/5gBItZR1qqhZ6+EbIzE5k8KZX4OJFQqB+NWiYvL48du+xs39WBxxtClmHq5DTu+eFK7n/gjzgcw9xyyzcpm1xIenp0/f25QJJkHn1qB/UNfdx1+3LSUi14vUG++h+PE4lEcLqDXLiwhKWLS/nPH73Amy/fyW//8DYGvRZJho1bjhMfpyc3J4llS8t4+bWDDDu89Pe5uHHdQtyeAJu3Hicrw8baa+fy5a8/ysL5RbS1DfCt21cwMuLj6ed2k5IUz6yZeaSkmHnltUP4/UFysq2svmw6f7x/Izqtmu5eB1+8dj6VldncescTTK/IpbXFzpqrZ9HaZqf6WBdanZKKKdksXTKZbTvqOXqsg6LCFBbMK+IvD75HSrKJQ4c7mD4tG/uAi8UXlnL7rRcTjoj09I7w4MNbaWjsJxAKM2dWAVPLM9jw7nG8/iAatZIffm9VNKpOELj0qt8zb3YBlVOy0RvV/P5P73DrTRfxP79+g8mT0tFp1fT1OzGb9XzxunlctLiUw0c7+fmv3+CSpeVYLHp+9JMXeee1u1n/7B4OHGzBaNRy6fKpZKQn8OiTOwiFRJYsmoRarWDDxmOExagx8Wc/voo/P7gZrUZNZ/cwWZmJfPXGRfz6D+/w8F++xIN/20pqSjyJCUZefeMw4bDIlZdPp66hhy3b66mYkklb+xA+b5Cvf3Ux23fUM+L0M2h3c/NXFtHeMcQbbx4lLSOenCwbtXU9XHvNHFZfXonuI3iI/hnO3fD2AeTn51JcVMj0aTOora2hr6+T+bNzMBo16HQqFsxOQwo3cGB/C129Cax/roe/PLwftyvILTct4c+/XcvXv7yItDQLM6blUl6ajjXRSEqahUsumozZpCMlOY6lF02muDAFnVZFcVEqP7/3c9x202Kuv2YORoOOx/9+nFffHOF4nYbde1tQ0kF5qRmTMRo2vGJZCcPDg2x89y1WX7EGqzWetLQzp6L6pEREkXAogkatRK2OGuxOSuH/uOVivv6VC+noGEKSRrMEyyCK0RparYqLFk/m9tuWodEqqdrVQHKSmZ/86EoqKjIJRyJs2nyCm9ZdyO9+dS06rQajTs0ffn09C+dP4uDhNg4daae8NIPMzATqGnvZs6eZRfOL+eNv1uLxBGnvGESSJL7/nctY+4V5NLcOsOHdY1y8uIxf3LuG3LxoyG2cWcdVV07nKzdeSFiUkCSJgvxkSorTsNvdeDxBjAYNP/3x1RQVJnPV6hl8ce0CmlrtbN/ZwMN/28477x7H5fbzw+9fzpWrpiFGIuzc08S0aTk88IcvolIrqKnrGRc12d/vpK1jkPDokuyIKFJWmsa66+ejUApUVmSj1SoZsLvG4gxCYZGO7iFa2weRpOhXrF977TDz5xVTVJDK0eouEhKMzJtTiMmko6VtkNr6Pi65eAo/+t4q8rJtNDUP4PeF+cVPPse1pyRXZXQNiihFMx+npVqYMS0HtUrJwIATUZS4etU0fvLDK7lq1TQuWlLKrOl57NzbzIJ5hVROzWL33iaUCoEZM7L55U+uQatVkZmZSGqK+ZxqoGfj/O8B0Gq1FJcUMX36DCRJpLW1icL8eJKtRpYtLuTaayoJBUVeeL2TV9+qZmDIE02MoVLQ0+vg4OE2UlPjyc9Noq6hl9kz8/jON5ZTmJPExq21xBm1rF0zh63b67j0kqnkZFkRwxKDdje2pDhUSgVFhamkp8Yz7PSzc28Hu/d7cLrCrLq0hIXzsslMj6OwwMLmzdGUYlnZ2RQU5J5zVUyjVpGbbWPY4WV7VT2NTf0MD3uRETAYNKjV0RBlnVZNOCzS2mant9cJghD1yes1KJUCKqUSvUGDPxCisakfx4gfEEiwGujpG6G51U44IqI36FAqBFQqAZVCQXxcNBCmpCiVZUsmk5hoxOH00djcj0KlQKdTo1Wr0Gmj4cyCIGBNNDEw4KK51T4WGKRSKdHr1CgVAkqFgk3v1XLwcNtojv5o5mTDqEquVCnR66LnplQqyM5KZPr0HHJyrKjVKtrbhxge9iIoBCxmPW6Xj4bGfuQIGPXasQhHQRC4ctV0/uOWi0iwGBGEaIi5Ua+NelUMWpQKgQvmFTO1PDNqEBXAEq/n5i8t4lv/sQydTo0gQFKqGUGIrtOfPTOXDe8eG80pYEGlEtDpNAw7fLR3DBEIhqNquQJa24cYGHQDoNWq8QeCtLbasQ+46Olx8OaGowQCEVKSzWPCPSHBiE6nRqNR4XZH8zZaLAZkGaaUZ7L84nJUaiVJSWaSk+L43BUzMJu0vPr6IXr7oklkzyf/EiEAkJKSTHJyEsVFk2hpaUaWPVyyNJ8Vy3LZu7eKpuP7KSl4P31XdP2AjFKpJCfHSnfvCB2dQ+zY2YgsyyjVKmQFKFVKfIEwr7x5hIryLJ79x15GRnw0tg6wZ38zwmi022tvHaH1lAUrKUk6elqOc/TQbhbNs7J8SRahoIetW7ewcNESzCYT8ebz47OdN6eQhfOL2fheDb+7bwMHDrWSn5eE2aTHmmiiuCi6mKh8cgaPPbkDs1lLZkYCGWnxZKYnEG/Wk5trY+7sAhLijbzy+mFa2gYwGjTc8IX51NT28NdHtiKKItMrs1EoBLKzrJSWprH0ojLCEZH6xj4kSWbZ0jI8ngDPvrCPaVNzKC/LZPLkTPR6DWkp0Xx5Ky+ZSjAscv/DW3B7AphMWrIzE0lONmNNNJKXa2NKWSZ6rZre3hFsNhM2WxzFk1LRaFSUTUonIcGAzRrHpKI0igtTWbSgmPlzC5lWkcXm907Q1++kqCiVlZdMRZJknli/k0mT0pg6NWssXmJqeSYJCUYEBMxmHVPKsrBZTRQVppCXa2Pm9DwcI1GBFghEUCoVxBm1lJakotNFbQszp+di0Gu57atLaGsfpLnVjqBQkJdnY8TpxecLUTopgwXzCui3u9i0tQab1UTFlEzmzy3imRf2cORoB4ym/8rPtfH8S/swx+nGckL2DzgRRZGMdAs5OUmkpERDwssmZxAMhqlv6OOmLy7kRF0PtfW9AKSnJ5CVmYhjxBdddxGMMKU8C+sZ8j+ca/4lNoGTHDpUzTvvvMu2bVu46sqrsNmS2L9/L5ufeZILUhJQXfRNnn+1cay+Jd7A8qVlVJRn0tM7wo5dDVSf6OaL185FEiVys2288MoBDAYNU8uzMOo1uD0BDlV3MDTs5cs3LGB4yIPBqOWJp3fhcEYzuyiVArPKNWQ0vcWBvh5KV1zOlGnT0Wq0fOd7d/PgI+uZVjmFooLT196fS8JhcSxASRBAEKIGNUkGpSKaLPPk9jGi67KQZXA6fdQ19tHZNcz2qnqu//xc5szOj7rbRHksJFehiK7gZHQ0jYx+3UY3anSLREREUR47DlmWx45FlsHnD/HOxuNEIiJbttby7W+toDA/msaM0emMQDQlmjD6wRRh1EWpUETV7+ho/v65nUSSZCKRqBvzpBsuet4iavV4K3rUhfi++zN6nAKyHD1HWZajmZuEaCam9+tFtzPqijy5n1BIRJIktFp11BUoiigViuh3GUenESc/ABPVCGX8gTCbR5OC/vHX1592j+ST7l6VAsXosTF6DxhdjahURg2pwVAEWZLR6Ua9YqPXMRKJfm9Rq41qLeeb8+odmIjD4WBocJh9+/YQH2/m2LFqDrzxMt/ITeZqvZqj1iTaelVjc0BBIRBn0mEx6+jrG6Kruw9kP319Pbjdg9TXN+P1jeD3uWjv6KW1vZeevmGQZSzxRvS6aH651rZBaht7EUe/EGNNNJBvGuJ6TzsZ7hE2NTQyJEoolCqqdlbx5ZtvJSUpkfj4T5ZK7KNy8mE4+VCefMBPqr8KhYBKFX0Az1SCoQiNjX10dA4zf24hMypz0Oui4bgnVfnow/u+X1wQovtVj26P7kdxhv283yYcFtm9twm3J8Dyi8uZVhHVLibWVyqjGX9Pbc+o12XiuZ1EGH3JTvYXPZ7o1Ofk71Prnvxv/L7f/0+lUqAae2nHt2G075O/379Opx+HIAioznA+JwWlLdFEYUHKafdIoRjt5wzHx+g06uQ8XzW6f85wf04e17+Cf6kmUHOijj17D/DnP/+BOJMReju4Kc3CckHiRHM7D06egzJlNfsOdWBNMJKYqEMpBBAII8shJNGFVu3HatWTmBhPXJwJg06PRqNFoVCh1RpQqrR4vSJdPS7sQ14iYQl/UMYXUGC3exke8VFSaCHBv5+r/G3McjnZNOjg0bCAYcp0Dhw6yPMvvU1RQTY5WecuNiBGjP+r/MtsAgCBYBCFIKBWqwm01PPlNAtLZZFjLR3cJyrwqbVMLbMwf3Y6ZSV60pJlzHEyoZCP7l4HLW0uevplAqEEdIYszAm5xCfmYIrPRGdIIyKZ6e0XOXyslx276zh2ohWPz02iRUF6MhTmqphSGk92hhIhycIbAZEacxzLbAncpJJxHj2IzZaMLEMoOH5NeowYn1b+ZZqAKIpU7djNxk2bqd/yNivVIZZGQtR19vDnoIw0cwGrLr8Cl9tHOGLk4JFOTtQOEAxrAM2YpVUQQK2W0WllNOpovLxapUKhVCNKSjyeCE5XYNwiGIEwGnWQovwEpk3NwJqoIisrlaqqbQxVbeQGo4oyp4uN9mFesKRy8dfuYNGiC5kxrXSsjxgxPq38y2wC4XCYjZs2c3zDa6xQhlgcClDX08fvRnx0peUwc9Ys4uPjMRgMxMUlYjAmodYYcXsiY2mqTiKKAsGQgM8v4PGC0y0x4grjcofGQpFPIghgNhuYOiWPuXMmM7U8h/T0BFQqFRqtnj2NLRzt6SY/KYG5KgXGwQG29XSjTkpl5owPDkmNEePTwL9EExBFkR07dvDaA39m6kAHiwJeGvoGeDyi5KBCR0JyMvEWCxq1BoPBSFZ2DlOmTCfekkFz6wh797dxvLb3tNxxH4ZGrSQ/z8LsGRmUliSjVPhpbKylva0Vp9NFJCIyNDSI2zlCoRzgNpuJScMONg0MsblkKtf+53+xfPnyid3GiPGp4rwLAUmSqKqqYsPfHqS0u4X5XhdN/XYejygYzC1GG2dGqVRhijNjMBhRq9R4fV7cbhdWq43Fi5eRnJLPoaPdvLPxOG2j0XQfhCAI2BK1zKhMYfIkKwqFh6NHDtLb240syUQiEZRKJVqtFpVKTVxcHB63C5qO880kE/mDw2wbHGFH+XSuvPPumCCI8anmvAoBWZbZu3cvrz7wZyZ1N7NwVAC8ZrahmXch+aWTSc9Ix2a1odMborP3UISu7l5a2tpoa23GPtDHtGkVLFt+OU6Xgi3v1bJjZyP9o4toJhJv1lBWkkDZ5ETMJpkTJw7R1NiA1WrFZrWSlJREVnY2qWmpxMXFoVAo8Hm9DA05aGlu4virz/ONBC05g8NUDTnZWTGTq+/6LkuWLJm4qxgxPhWcVyHg9Xp59uEHsa9/hGuUMi32QV4zJ7Hgzu8y98LFGI1G9Ho9Wm10pZQoSkQiYby+AL29dppb2mhqbuJ49WEi4QAXL11G6eQZOBwhTtR209DUx+CQm0gkglYrkJqsJz3NgNmkpLOzgf379mI2mykrKyMzM4uCgjzy8/NJSEhAb9CjVkcXZoTDYYLBIJFwhL17dvPkPf/FHVYdWYMONjq9HF15NX/805/H+XtjxPi0cF6FQDgc5pmnnmTfb3/JFJ+TarOVBXfczWWfW0N8fPSz1mdClmWCwRBOp4f2rj66urpoba5n756dSKLI3LkLKJ08FZVKj9vtxePxEAj48PmctLbWc/jwIbRaLfPnzaeoqJj09HTyC/JITk7CYDB84KKMUCjExnfe4fEf/SdXq0WOugLEf+lrfP8HP5hYNUaMTwXnVQgADAwM8Przz3F0z26WrFrNRSsu/UABcCqSJBEMhnG5vYyMjOByjVBXW8POnVWjGYdDaDUaIqKEy+VCrVZRVlbG3DnzKC4uId4ST2ZmBklJ1mhKsVO+cfBBBAIBtm99j9efXk9J+RSuvenm6MdQYsT4FHLehYAsy/j9fgKBAAaDYfQrQB8PSYouVY2IIoFgEK/Xi9fjwT5gp6+/n0gkgi3RSny8BYVSRVxcHAmWeExxBtRq9Ud++U8lHA7jcrnQarWYTOdnIVGMGP8XOO9C4FwTPVoZURQJh8OEwmEkUUKpVKJUKlGr1afFzceIEePs/NsJgRgxYpxbzm4hixEjxmeCmBCIEeMzTkwIxIjxGScmBGLE+IwTEwIxYnzGiQmBGDE+48SEQIwYn3H+Hxm32Ut1FbrxAAAAAElFTkSuQmCC"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================
# 세션 초기화
# ============================================================
if "users" not in st.session_state:
    st.session_state.users = {
        "qhtjd0611": {
            "password_hash": hash_password("kyn04228@@"),
            "role": "admin",
            "name": "최고관리자",
            "created_at": "2024-01-01"
        }
    }
if "login_user" not in st.session_state:
    st.session_state.login_user = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = []
if "resources" not in st.session_state:
    st.session_state.resources = []
if "faq_counts" not in st.session_state:
    st.session_state.faq_counts = {
        "병가": 0, "공가": 0, "초과근무": 0,
        "e사람": 0, "온나라": 0, "e호조": 0,
        "법령": 0, "조례": 0,
    }

# ============================================================
# 색상
# ============================================================
NAVY = "#1C3A5C"
NAVY_DARK = "#162844"
LIGHT_BG = "#F8F8F6"
WHITE = "#FFFFFF"
TEXT_DARK = "#333333"
TEXT_GRAY = "#666666"
BORDER_GRAY = "#DDDDDD"

# ============================================================
# CSS
# ============================================================
st.markdown(f"""
<style>
    * {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', '나눔고딕', sans-serif;
    }}
    .stApp {{ background-color: {LIGHT_BG}; }}

    /* 사이드바 */
    section[data-testid="stSidebar"] {{ background-color: {NAVY}; }}
    section[data-testid="stSidebar"] * {{ color: {WHITE} !important; }}

    /* 사이드바 메뉴 라벨 텍스트 */
    .menu-label {{
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 1px;
        color: rgba(255,255,255,0.6) !important;
        margin: 8px 0 12px 4px;
    }}

    /* 네모 박스형 메뉴 버튼 */
    section[data-testid="stSidebar"] div[role="radiogroup"] {{
        gap: 8px;
        display: flex;
        flex-direction: column;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 14px 16px !important;
        margin: 0 !important;
        cursor: pointer;
        transition: all 0.15s ease;
        font-size: 15px !important;
        font-weight: 600 !important;
        width: 100%;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
        background: rgba(255,255,255,0.15);
        border-color: rgba(255,255,255,0.35);
    }}
    /* 라디오 동그라미 숨기기 */
    section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{
        display: none !important;
    }}
    /* 선택된 항목 - 남색 채움(살짝 밝게) */
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{
        background: {WHITE};
        border-color: {WHITE};
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {{
        color: {NAVY} !important;
        font-weight: 700 !important;
    }}

    /* 정보 박스 */
    .info-box {{
        background: {WHITE};
        border: 1px solid {BORDER_GRAY};
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .info-box-title {{
        color: {NAVY};
        font-weight: 700;
        font-size: 20px;
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 2px solid {NAVY};
    }}
    .info-box p {{
        color: {TEXT_DARK};
        font-size: 15px;
        line-height: 1.7;
        margin: 0;
    }}

    /* 버튼 */
    .stButton > button {{
        background-color: {NAVY};
        color: {WHITE};
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover {{
        background-color: {NAVY_DARK};
        box-shadow: 0 2px 6px rgba(28,58,92,0.3);
        color: {WHITE};
    }}

    /* 입력 필드 */
    div[data-testid="stTextInput"] input {{
        border: 1px solid {BORDER_GRAY} !important;
        border-radius: 6px !important;
    }}

    /* 메인 탭 (관리자) */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {NAVY};
        border-bottom-color: {NAVY};
    }}

    /* 상태 배지 */
    .badge {{
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 13px;
    }}
    .badge-wait {{ background: #FFF3CD; color: #856404; }}
    .badge-ok {{ background: #D4EDDA; color: #155724; }}
    .badge-no {{ background: #F8D7DA; color: #721C24; }}
    .badge-hold {{ background: #E2E3E5; color: #383D41; }}

    /* 사이드바 사용자 정보 */
    .user-card {{
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 16px;
    }}
    .user-card .label {{
        color: rgba(255,255,255,0.6) !important;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }}
    .user-card .value {{
        color: {WHITE} !important;
        font-weight: 700;
        font-size: 16px;
    }}
    .user-card .divider {{
        margin: 12px 0;
        border-top: 1px solid rgba(255,255,255,0.15);
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 유틸
# ============================================================
def get_role():
    return st.session_state.users[st.session_state.login_user]["role"]

def is_admin():
    return get_role() == "admin"

def logo_html(width=240):
    return f'<img src="data:image/png;base64,{LOGO_B64}" style="width:{width}px;max-width:100%;height:auto;">'

def classify_question(q: str):
    q = q.lower()
    categories = {
        "병가": ["병가"], "공가": ["공가"], "초과근무": ["초과", "시간외"],
        "e사람": ["e사람"], "온나라": ["온나라"], "e호조": ["e호조"],
        "법령": ["법", "법령"], "조례": ["조례"]
    }
    for category, keywords in categories.items():
        if any(k in q for k in keywords):
            return category
    return "기타"

def status_badge(status):
    cls = {"승인대기": "badge-wait", "승인완료": "badge-ok", "반려": "badge-no", "보류": "badge-hold"}.get(status, "badge-wait")
    return f'<span class="badge {cls}">{status}</span>'

# ============================================================
# 로그인 페이지
# ============================================================
def login_page():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f'<div style="text-align:center;padding:30px 0 10px 0;">{logo_html(280)}</div>',
            unsafe_allow_html=True
        )
        st.markdown(f"""
        <div style="text-align:center;padding:8px 0 20px 0;">
            <div style="font-size:22px;font-weight:700;color:{TEXT_DARK};margin-bottom:8px;">충남119 복무AI</div>
            <div style="font-size:14px;color:{TEXT_GRAY};">충남 소방공무원을 위한 업무 정보 안내 서비스</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        with tab1:
            st.markdown("### 로그인")
            login_id = st.text_input("아이디", key="login_id")
            login_pw = st.text_input("비밀번호", type="password", key="login_pw")
            if st.button("로그인", use_container_width=True):
                if not login_id or not login_pw:
                    st.error("아이디와 비밀번호를 입력하세요.")
                elif login_id in st.session_state.users:
                    if st.session_state.users[login_id]["password_hash"] == hash_password(login_pw):
                        st.session_state.login_user = login_id
                        st.rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                else:
                    st.error("존재하지 않는 아이디입니다.")
        with tab2:
            st.markdown("### 회원가입")
            sid = st.text_input("새 아이디", key="signup_id")
            spw = st.text_input("새 비밀번호", type="password", key="signup_pw")
            if st.button("회원가입", use_container_width=True):
                if not sid or not spw:
                    st.warning("모든 항목을 입력하세요.")
                elif len(sid) < 6 or len(spw) < 6:
                    st.warning("아이디와 비밀번호는 6자 이상이어야 합니다.")
                elif sid in st.session_state.users:
                    st.error("이미 사용 중인 아이디입니다.")
                else:
                    st.session_state.users[sid] = {
                        "password_hash": hash_password(spw),
                        "role": "user",
                        "name": sid,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    st.success("회원가입이 완료되었습니다. 로그인해주세요.")

# ============================================================
# 홈
# ============================================================
def home_page():
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-title">질문하기</div>
            <p>복무규정, 병가, 공가, 초과근무 등 일상 업무 중 궁금한 사항을 편하게 물어보세요.</p>
        </div>
        """, unsafe_allow_html=True)

        question = st.text_input(
            "질문", placeholder="예: 당직근무 중 병가를 쓰면 어떻게 처리해?",
            label_visibility="collapsed"
        )
        if question:
            category = classify_question(question)
            if category in st.session_state.faq_counts:
                st.session_state.faq_counts[category] += 1
            st.markdown(f"""
            <div class="info-box">
                <div class="info-box-title">답변</div>
                <p><strong>분류:</strong> {category}</p>
                <p>현재 Gemini API 연동 작업 중입니다. 다음 업데이트에서 실시간 AI 답변이 제공될 예정입니다.</p>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="info-box"><div class="info-box-title">인기 질문</div>', unsafe_allow_html=True)
        ranked = sorted(st.session_state.faq_counts.items(), key=lambda x: x[1], reverse=True)
        any_q = False
        for i, (name, cnt) in enumerate(ranked[:5], 1):
            if cnt > 0:
                any_q = True
                st.markdown(f"**{i}. {name}** · {cnt}회")
        if not any_q:
            st.markdown(f'<p style="color:{TEXT_GRAY};font-size:14px;">아직 질문 기록이 없습니다.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# 법령·조례
# ============================================================
def law_page():
    st.markdown(f"""
    <div class="info-box">
        <div class="info-box-title">법령·조례·매뉴얼</div>
        <p>현재 등록·승인된 자료 목록입니다.</p>
    </div>
    """, unsafe_allow_html=True)
    if not st.session_state.resources:
        st.info("등록된 자료가 없습니다.")
    else:
        for r in st.session_state.resources:
            st.markdown(f"""
            <div class="info-box">
                <p style="font-size:16px;font-weight:700;color:{TEXT_DARK};margin-bottom:6px;">{r['name']}</p>
                <p style="color:{TEXT_GRAY};font-size:13px;">{r['category']} · 등록일 {r['date']}</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# 건의·신청
# ============================================================
def suggestion_page():
    st.markdown(f"""
    <div class="info-box">
        <div class="info-box-title">자료 신청</div>
        <p>필요한 법령, 조례, 매뉴얼을 신청하실 수 있습니다. 관리자 승인 후 목록에 등록됩니다.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("suggestion_form", clear_on_submit=True):
        a, b = st.columns(2)
        with a:
            title = st.text_input("자료 제목")
        with b:
            category = st.selectbox("자료 종류", ["법령", "조례", "지침", "매뉴얼", "기타"])
        content = st.text_area("신청 사유", height=100)
        file = st.file_uploader("파일 첨부 (선택)", type=["pdf", "doc", "docx"])
        if st.form_submit_button("신청 제출", use_container_width=True):
            if not title:
                st.error("제목을 입력하세요.")
            else:
                st.session_state.suggestions.append({
                    "id": len(st.session_state.suggestions) + 1,
                    "title": title, "category": category, "content": content,
                    "file_name": file.name if file else "첨부 없음",
                    "status": "승인대기", "user": st.session_state.login_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("신청이 완료되었습니다.")

    st.markdown("### 내 신청 목록")
    mine = [x for x in st.session_state.suggestions if x["user"] == st.session_state.login_user]
    if not mine:
        st.info("신청한 자료가 없습니다.")
    else:
        for item in mine:
            st.markdown(f"""
            <div class="info-box">
                <p style="font-size:16px;font-weight:700;color:{TEXT_DARK};margin-bottom:6px;">{item['title']}</p>
                <p style="color:{TEXT_GRAY};font-size:13px;margin-bottom:10px;">{item['category']} · {item['file_name']} · {item['date']}</p>
                {status_badge(item['status'])}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# 관리자
# ============================================================
def admin_page():
    st.markdown(f'<div class="info-box-title" style="font-size:22px;">신청 자료 관리</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["신청 관리", "자료 등록"])

    with tab1:
        wait = len([x for x in st.session_state.suggestions if x["status"] == "승인대기"])
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-title">신청 현황</div>
            <p>총 {len(st.session_state.suggestions)}건 · 대기 {wait}건</p>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.suggestions:
            st.info("신청 자료가 없습니다.")
        else:
            for i, item in enumerate(st.session_state.suggestions):
                st.markdown(f"""
                <div class="info-box">
                    <p style="font-size:16px;font-weight:700;color:{TEXT_DARK};margin-bottom:6px;">{item['title']}</p>
                    <p style="color:{TEXT_GRAY};font-size:13px;margin-bottom:10px;">신청자 {item['user']} · {item['category']} · {item['date']}</p>
                    {status_badge(item['status'])}
                </div>
                """, unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("승인", key=f"ap_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "승인완료"
                        if not any(r["name"] == item["title"] for r in st.session_state.resources):
                            st.session_state.resources.append({
                                "name": item["title"], "category": item["category"],
                                "date": datetime.now().strftime("%Y-%m-%d")
                            })
                        st.rerun()
                with col2:
                    if st.button("반려", key=f"rj_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "반려"
                        st.rerun()
                with col3:
                    if st.button("보류", key=f"hd_{i}", use_container_width=True):
                        st.session_state.suggestions[i]["status"] = "보류"
                        st.rerun()

    with tab2:
        st.markdown(f"""
        <div class="info-box">
            <div class="info-box-title">새 자료 등록</div>
            <p>관리자가 직접 자료를 등록하면 즉시 법령·조례 목록에 표시됩니다.</p>
        </div>
        """, unsafe_allow_html=True)
        with st.form("add_resource", clear_on_submit=True):
            rt = st.text_input("자료명")
            rc = st.selectbox("자료 종류", ["법령", "조례", "지침", "매뉴얼", "기타"], key="rc")
            if st.form_submit_button("자료 등록", use_container_width=True):
                if not rt:
                    st.error("자료명을 입력하세요.")
                else:
                    st.session_state.resources.append({
                        "name": rt, "category": rc,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.success("자료가 등록되었습니다.")

        st.markdown("### 등록된 자료 목록")
        if not st.session_state.resources:
            st.info("등록된 자료가 없습니다.")
        else:
            for i, r in enumerate(st.session_state.resources):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"**{r['name']}**  ·  {r['category']}  ·  {r['date']}")
                with col2:
                    if st.button("삭제", key=f"del_{i}", use_container_width=True):
                        st.session_state.resources.pop(i)
                        st.rerun()

# ============================================================
# 메인
# ============================================================
if st.session_state.login_user is None:
    login_page()
else:
    with st.sidebar:
        st.markdown(f'<div style="padding:12px 0 20px 0;">{logo_html(190)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="menu-label">메뉴</div>', unsafe_allow_html=True)

    menu_list = ["홈", "법령·조례", "건의·신청"]
    if is_admin():
        menu_list.append("관리자")
    selected = st.sidebar.radio("메뉴", menu_list, index=0, label_visibility="collapsed")

    # 헤더
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(f"""
        <div style="padding:18px 24px;background:{WHITE};border:1px solid {BORDER_GRAY};border-radius:8px;">
            <div style="font-size:20px;font-weight:700;color:{TEXT_DARK};">충남119 복무AI</div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        if st.button("로그아웃", use_container_width=True):
            st.session_state.login_user = None
            st.rerun()

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    if selected == "홈":
        home_page()
    elif selected == "법령·조례":
        law_page()
    elif selected == "건의·신청":
        suggestion_page()
    elif selected == "관리자":
        admin_page()

    # 사이드바 사용자 정보
    with st.sidebar:
        st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="user-card">
            <div class="label">현재 사용자</div>
            <div class="value">{st.session_state.login_user}</div>
            <div class="divider"></div>
            <div class="label">권한</div>
            <div class="value">{'관리자' if is_admin() else '일반사용자'}</div>
        </div>
        """, unsafe_allow_html=True)

    # 푸터
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center;color:{TEXT_GRAY};font-size:12px;padding:16px 0;">
        충남119 복무AI v3.0 · 충남소방본부 · {datetime.now().strftime('%Y년 %m월 %d일')}
    </div>
    """, unsafe_allow_html=True)
